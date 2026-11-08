// minimal scripted libretro frontend
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdbool.h>
#include "libretro.h"
#include <execinfo.h>
#include <signal.h>
#include <unistd.h>
static void segv(int s){void*b[64];int n=backtrace(b,64);backtrace_symbols_fd(b,n,2);_exit(1);}
static void *core;
#define SYM(n) n##_t n = (n##_t)dlsym(core,#n)
typedef void (*retro_init_t)(void); typedef void (*retro_deinit_t)(void);
typedef void (*retro_run_t)(void); typedef bool (*retro_load_game_t)(const struct retro_game_info*);
typedef void (*retro_set_environment_t)(retro_environment_t);
typedef void (*retro_set_video_refresh_t)(retro_video_refresh_t);
typedef void (*retro_set_audio_sample_t)(retro_audio_sample_t);
typedef void (*retro_set_audio_sample_batch_t)(retro_audio_sample_batch_t);
typedef void (*retro_set_input_poll_t)(retro_input_poll_t);
typedef void (*retro_set_input_state_t)(retro_input_state_t);
typedef void* (*retro_get_memory_data_t)(unsigned); typedef size_t (*retro_get_memory_size_t)(unsigned);
typedef size_t (*retro_serialize_size_t)(void); typedef bool (*retro_serialize_t)(void*,size_t); typedef bool (*retro_unserialize_t)(const void*,size_t);
typedef void (*retro_set_controller_port_device_t)(unsigned,unsigned);
static unsigned fbw,fbh; static size_t fbpitch; static uint8_t fb[1024*1024*4]; static int pixfmt=0;
static uint32_t buttons=0;
static const char *sysdir;
static void logcb(enum retro_log_level l,const char*f,...){ if(l<RETRO_LOG_WARN && !getenv("ALLLOG")) return; va_list a; va_start(a,f); vfprintf(stderr,f,a); va_end(a);}
static bool env(unsigned cmd,void*data){
  switch(cmd){
   case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY: case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY: *(const char**)data=sysdir; return true;
   case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT: pixfmt=*(int*)data; return true;
   case RETRO_ENVIRONMENT_GET_LOG_INTERFACE: ((struct retro_log_callback*)data)->log=logcb; return true;
   case RETRO_ENVIRONMENT_GET_VARIABLE: {
     struct retro_variable *v=data;
     if(!strcmp(v->key,"pcsx_rearmed_bios")){v->value="HLE";return true;}
     if(!strcmp(v->key,"pcsx_rearmed_drc")){v->value="disabled";return true;}
     if(!strcmp(v->key,"neocd_bios")&&getenv("NEOBIOS")){v->value=getenv("NEOBIOS");return true;}
     if(!strcmp(v->key,"neocd_cdspeedhack")||!strcmp(v->key,"neocd_loadskip")){v->value=getenv("NGSLOW")?"Off":"On";return true;}
     if(!strcmp(v->key,"pcsx_rearmed_memcard1")){v->value="libretro";return true;}
     if(!strcmp(v->key,"pcsx_rearmed_memcard2")){v->value="none";return true;}
     v->value=NULL; return false;}
   case RETRO_ENVIRONMENT_GET_CAN_DUPE: *(bool*)data=true; return true;
   default: return false;
  }
}
static void video(const void*data,unsigned w,unsigned h,size_t pitch){
  if(!data) return; fbw=w; fbh=h; fbpitch=pitch;
  for(unsigned y=0;y<h;y++) memcpy(fb+y*pitch,(const uint8_t*)data+y*pitch,pitch);
}
static void aud(int16_t l,int16_t r){} static size_t audb(const int16_t*d,size_t f){return f;}
static void poll(void){}
static long qcount=0;
static int16_t inst(unsigned port,unsigned dev,unsigned idx,unsigned id){ qcount++;
  if(port) return 0;
  if(id==RETRO_DEVICE_ID_JOYPAD_MASK) return buttons;
  int16_t r=(buttons>>id)&1; return r;
}
static void shot(const char*fn){
  FILE*f=fopen(fn,"wb"); fprintf(f,"P6\n%u %u\n255\n",fbw,fbh);
  for(unsigned y=0;y<fbh;y++) for(unsigned x=0;x<fbw;x++){
    uint8_t r,g,b;
    if(pixfmt==RETRO_PIXEL_FORMAT_XRGB8888){uint32_t p=*(uint32_t*)(fb+y*fbpitch+x*4); r=p>>16;g=p>>8;b=p;}
    else {uint16_t p=*(uint16_t*)(fb+y*fbpitch+x*2); if(pixfmt==RETRO_PIXEL_FORMAT_RGB565){r=(p>>11)<<3;g=((p>>5)&63)<<2;b=(p&31)<<3;} else {r=((p>>10)&31)<<3;g=((p>>5)&31)<<3;b=(p&31)<<3;}}
    fputc(r,f);fputc(g,f);fputc(b,f);}
  fclose(f);
}
static int bid(const char*n){
  const char*names[]={"B","Y","SELECT","START","UP","DOWN","LEFT","RIGHT","A","X","L","R","L2","R2","L3","R3"};
  for(int i=0;i<16;i++) if(!strcmp(n,names[i])) return i; return -1;}
int main(int argc,char**argv){
  // argv: core rom sysdir  ; commands on stdin
  signal(SIGSEGV,segv);
  core=dlopen(argv[1],RTLD_NOW); if(!core){fprintf(stderr,"%s\n",dlerror());return 1;}
  sysdir=argv[3];
  SYM(retro_set_environment); SYM(retro_set_video_refresh); SYM(retro_set_audio_sample); SYM(retro_set_audio_sample_batch);
  SYM(retro_set_input_poll); SYM(retro_set_input_state); SYM(retro_init); SYM(retro_load_game); SYM(retro_run);
  SYM(retro_get_memory_data); SYM(retro_get_memory_size); SYM(retro_serialize_size); SYM(retro_serialize); SYM(retro_unserialize);
  SYM(retro_set_controller_port_device);
  retro_set_environment(env); retro_set_video_refresh(video); retro_set_audio_sample(aud); retro_set_audio_sample_batch(audb);
  retro_set_input_poll(poll); retro_set_input_state(inst); retro_init();
  struct retro_game_info gi={argv[2],NULL,0,NULL};
  if(!retro_load_game(&gi)){fprintf(stderr,"load failed\n");return 1;}
  if(getenv("MCD")){ uint8_t*m=retro_get_memory_data(RETRO_MEMORY_SAVE_RAM); size_t ms=retro_get_memory_size(RETRO_MEMORY_SAVE_RAM); FILE*mf=fopen(getenv("MCD"),"rb"); if(m&&mf){size_t r=fread(m,1,ms,mf); fprintf(stderr,"mcd loaded %zu/%zu\n",r,ms);} if(mf)fclose(mf);}
  retro_set_controller_port_device(0,RETRO_DEVICE_JOYPAD);
  char line[512]; long frame=0;
  while(fgets(line,sizeof line,stdin)){
    char a[256],b[256]; long n;
    if(sscanf(line,"run %ld",&n)==1){ for(long i=0;i<n;i++){retro_run();frame++;} }
    else if(sscanf(line,"press %s %ld",a,&n)==2){ int id=bid(a); buttons|=1u<<id; for(long i=0;i<n;i++){retro_run();frame++;} buttons&=~(1u<<id); }
    else if(sscanf(line,"hold %s",a)==1){ buttons|=1u<<bid(a);} 
    else if(sscanf(line,"release %s",a)==1){ buttons&=~(1u<<bid(a));}
    else if(sscanf(line,"shot %s",a)==1){ shot(a); }
    else if(sscanf(line,"dumpram %s",a)==1){ FILE*f=fopen(a,"wb"); fwrite(retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM),1,retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM),f); fclose(f);}
    else if(sscanf(line,"save %s",a)==1){ size_t s=retro_serialize_size(); void*p=malloc(s); retro_serialize(p,s); FILE*f=fopen(a,"wb"); fwrite(p,1,s,f); fclose(f); free(p);}
    else if(sscanf(line,"load %s",a)==1){ FILE*f=fopen(a,"rb"); fseek(f,0,2); size_t s=ftell(f); fseek(f,0,0); void*p=malloc(s); fread(p,1,s,f); fclose(f); retro_unserialize(p,s); free(p);}
    else if(sscanf(line,"poke %s %s",a,b)==2){ unsigned long ad=strtoul(a,0,16)&0x1fffff; FILE*f=fopen(b,"rb"); uint8_t*ram=retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM); size_t n=fread(ram+ad,1,65536,f); fclose(f); fprintf(stderr,"poked %zu\n",n);}
    else if(sscanf(line,"dumpmem %ld %s",&n,a)==2){ FILE*f=fopen(a,"wb"); fwrite(retro_get_memory_data((unsigned)n),1,retro_get_memory_size((unsigned)n),f); fclose(f);}
    else if(!strncmp(line,"quit",4)) break;
    fprintf(stderr,"frame %ld q %ld\n",frame,qcount);
  }
  return 0;
}
