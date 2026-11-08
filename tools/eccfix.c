// Recompute EDC/ECC for Mode2 Form1 sectors (and EDC for Form2) in range [start,end) of a raw 2352 bin
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static uint8_t ecc_f[256],ecc_b[256]; static uint32_t edc_t[256];
static void init(void){ for(uint32_t i=0;i<256;i++){ uint32_t j=(i<<1)^((i&0x80)?0x11D:0); ecc_f[i]=j&0xff; ecc_b[i^(j&0xff)]=i; uint32_t e=i; for(int k=0;k<8;k++) e=(e>>1)^((e&1)?0xD8018001:0); edc_t[i]=e; } }
static uint32_t edc(const uint8_t*p,size_t n){ uint32_t e=0; while(n--) e=(e>>8)^edc_t[(e^*p++)&0xff]; return e; }
static void blk(const uint8_t*src,uint32_t majc,uint32_t minc,uint32_t majm,uint32_t mini,uint8_t*dst){
  uint32_t size=majc*minc;
  for(uint32_t ma=0;ma<majc;ma++){ uint32_t idx=(ma>>1)*majm+(ma&1); uint8_t a=0,b=0;
    for(uint32_t mi=0;mi<minc;mi++){ uint8_t t=src[idx]; idx+=mini; if(idx>=size) idx-=size; a^=t; b^=t; a=ecc_f[a]; }
    a=ecc_b[ecc_f[a]^b]; dst[ma]=a; dst[ma+majc]=a^b; } }
int main(int argc,char**argv){
  init(); FILE*f=fopen(argv[1],"r+b"); long s=atol(argv[2]), e=atol(argv[3]); uint8_t sec[2352]; long nf1=0,nf2=0;
  for(long l=s;l<e;l++){ fseek(f,l*2352,SEEK_SET); if(fread(sec,1,2352,f)!=2352) break;
    if(sec[15]!=2) continue;
    if(sec[18]&0x20){ uint32_t v=edc(sec+16,2332-4+4+0); /* form2: edc over 0x10..0x92B */ v=edc(sec+16,0x91C); 
       /* keep form2 untouched unless edc present nonzero */ nf2++; continue; }
    uint32_t v=edc(sec+16,0x808); sec[0x818]=v; sec[0x819]=v>>8; sec[0x81a]=v>>16; sec[0x81b]=v>>24;
    uint8_t h[4]; memcpy(h,sec+12,4); memset(sec+12,0,4);
    blk(sec+0xC,86,24,2,86,sec+0x81C); blk(sec+0xC,52,43,86,88,sec+0x8C8);
    memcpy(sec+12,h,4);
    fseek(f,l*2352,SEEK_SET); fwrite(sec,1,2352,f); nf1++; }
  fclose(f); printf("form1 %ld form2 %ld\n",nf1,nf2); return 0; }
