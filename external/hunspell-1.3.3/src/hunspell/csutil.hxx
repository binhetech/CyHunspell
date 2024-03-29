#ifndef __CSUTILHXX__
#define __CSUTILHXX__

#include "hunvisapi.h"

// First some base level utility routines

#include <string.h>
#include "w_char.hxx"
#include "htypes.hxx"

#ifdef MOZILLA_CLIENT
#include "nscore.h" // for mozalloc headers
#endif

// casing
#define NOCAP   0
#define INITCAP 1
#define ALLCAP  2
#define HUHCAP  3
#define HUHINITCAP  4

// default encoding and keystring
#define SPELL_ENCODING  "ISO8859-1"
#define SPELL_KEYSTRING "qwertyuiop|asdfghjkl|zxcvbnm" 

// default morphological fields
#define MORPH_STEM        "st:"
#define MORPH_ALLOMORPH   "al:"
#define MORPH_POS         "po:"
#define MORPH_DERI_PFX    "dp:"
#define MORPH_INFL_PFX    "ip:"
#define MORPH_TERM_PFX    "tp:"
#define MORPH_DERI_SFX    "ds:"
#define MORPH_INFL_SFX    "is:"
#define MORPH_TERM_SFX    "ts:"
#define MORPH_SURF_PFX    "sp:"
#define MORPH_FREQ        "fr:"
#define MORPH_PHON        "ph:"
#define MORPH_HYPH        "hy:"
#define MORPH_PART        "pa:"
#define MORPH_FLAG        "fl:"
#define MORPH_HENTRY      "_H:"
#define MORPH_TAG_LEN     strlen(MORPH_STEM)

#define MSEP_FLD ' '
#define MSEP_REC '\n'
#define MSEP_ALT '\v'

// default flags
#define DEFAULTFLAGS   65510
#define FORBIDDENWORD  65510
#define ONLYUPCASEFLAG 65511

// fopen or optional _wfopen to fix long pathname problem of WIN32
LIBHUNSPELL_DLL_EXPORTED FILE * myfopen(const char * path, const char * mode);

// convert UTF-16 characters to UTF-8
LIBHUNSPELL_DLL_EXPORTED char * u16_u8(char * dest, int size, const w_char * src, int srclen);

// convert UTF-8 characters to UTF-16
LIBHUNSPELL_DLL_EXPORTED int u8_u16(w_char * dest, int size, const char * src);

// sort 2-byte vector
LIBHUNSPELL_DLL_EXPORTED void flag_qsort(unsigned short flags[], int begin, int end);

// binary search in 2-byte vector
LIBHUNSPELL_DLL_EXPORTED int flag_bsearch(unsigned short flags[], unsigned short flag, int right);

// remove end of line char(s)
LIBHUNSPELL_DLL_EXPORTED void mychomp(char * s);

// duplicate string
LIBHUNSPELL_DLL_EXPORTED char * mystrdup(const char * s);

// strcat for limited length destination string
LIBHUNSPELL_DLL_EXPORTED char * mystrcat(char * dest, const char * st, int max);

// duplicate reverse of string
LIBHUNSPELL_DLL_EXPORTED char * myrevstrdup(const char * s);

// parse into tokens with char delimiter
LIBHUNSPELL_DLL_EXPORTED char * mystrsep(char ** sptr, const char delim);
// parse into tokens with char delimiter
LIBHUNSPELL_DLL_EXPORTED char * mystrsep2(char ** sptr, const char delim);

// parse into tokens with char delimiter
LIBHUNSPELL_DLL_EXPORTED char * mystrrep(char *, const char *, const char *);

// append s to ends of every lines in text
LIBHUNSPELL_DLL_EXPORTED void strlinecat(char * lines, const char * s);

// tokenize into lines with new line
LIBHUNSPELL_DLL_EXPORTED int line_tok(const char * text, char *** lines, char breakchar);

// tokenize into lines with new line and uniq in place
LIBHUNSPELL_DLL_EXPORTED char * line_uniq(char * text, char breakchar);
LIBHUNSPELL_DLL_EXPORTED char * line_uniq_app(char ** text, char breakchar);

// change oldchar to newchar in place
LIBHUNSPELL_DLL_EXPORTED char * tr(char * text, char oldc, char newc);

// reverse word
LIBHUNSPELL_DLL_EXPORTED int reverseword(char *);

// reverse word
LIBHUNSPELL_DLL_EXPORTED int reverseword_utf(char *);

// remove duplicates
LIBHUNSPELL_DLL_EXPORTED int uniqlist(char ** list, int n);

// free character array list
LIBHUNSPELL_DLL_EXPORTED void freelist(char *** list, int n);

// character encoding information
struct cs_info {
  unsigned char ccase;
  unsigned char clower;
  unsigned char cupper;
};

LIBHUNSPELL_DLL_EXPORTED int initialize_utf_tbl();
LIBHUNSPELL_DLL_EXPORTED void free_utf_tbl();
LIBHUNSPELL_DLL_EXPORTED unsigned short unicodetoupper(unsigned short c, int langnum);
LIBHUNSPELL_DLL_EXPORTED unsigned short unicodetolower(unsigned short c, int langnum);
LIBHUNSPELL_DLL_EXPORTED int unicodeisalpha(unsigned short c);

LIBHUNSPELL_DLL_EXPORTED struct cs_info * get_current_cs(const char * es);

// get language identifiers of language codes
LIBHUNSPELL_DLL_EXPORTED int get_lang_num(const char * lang);

// get characters of the given 8bit encoding with lower- and uppercase forms
LIBHUNSPELL_DLL_EXPORTED char * get_casechars(const char * enc);

// convert null terminated string to all caps using encoding
LIBHUNSPELL_DLL_EXPORTED void enmkallcap(char * d, const char * p, const char * encoding);

// convert null terminated string to all little using encoding
LIBHUNSPELL_DLL_EXPORTED void enmkallsmall(char * d, const char * p, const char * encoding);

// convert null t                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 