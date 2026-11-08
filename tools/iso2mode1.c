// convert 2048-byte ISO to MODE1/2352 raw bin with EDC/ECC
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
static uint8_t bcd(int n){return (uint8_t)(((n/10)<<4)|(n%10));}
int main(int argc,char**argv){
  init(); FILE*in=fopen(argv[1],"rb"); FILE*out=fopen(argv[2],"wb"); long minsec=argc>3?atol(argv[3]):0;
  uint8_t d[2048],s[2352]; long lba=0;
  for(;;){ size_t n=fread(d,1,2048,in); if(n==0 && lba>=minsec) break; if(n<2048) memset(d+n,0,2048-n);
    memset(s,0,2352); s[0]=0; memset(s+1,0xff,10); s[11]=0;
    long a=lba+150; s[12]=bcd(a/4500); s[13]=bcd((a/75)%60); s[14]=bcd(a%75); s[15]=1;
    memcpy(s+16,d,2048);
    uint32_t v=edc(s,2064); s[2064]=v; s[2065]=v>>8; s[2066]=v>>16; s[2067]=v>>24;
    blk(s+0xC,86,24,2,86,s+0x81C); blk(s+0xC,52,43,86,88,s+0x8C8);
    fwrite(s,1,2352,out); lba++; if(n<2048 && lba>=minsec) break; }
  fclose(out); printf("%ld sectors\n",lba); return 0; }
