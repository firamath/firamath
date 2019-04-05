% Turn off LaTeX2e messages
\def\e@alloc#1#2#3#4#5#6{%
  \global\advance#3\@ne
  \e@ch@ck{#3}{#4}{#5}#1%
  \allocationnumber#3\relax
  \global#2#6\allocationnumber
  }
\def\@pr@videpackage[#1]{%
  \expandafter\xdef\csname ver@\@currname.\@currext\endcsname{#1}}
\def\@providesfile#1[#2]{%
    \expandafter\xdef\csname ver@#1\endcsname{#2}%
  \endgroup}
\def\@latex@info#1{}
\def\@font@info#1{}
\def\ClassInfo#1#2{}
\def\PackageInfo#1#2{}

\RequirePackage{expl3}
\ProvidesExplClass{firamath-test}{}{}{}

\RequirePackage{ctexhook}

% Turn off LaTeX3 messages
\cs_new:Npn \@@_close_msg:nn #1#2
  { \msg_redirect_name:nnn {#1} {#2} { none } }
\@@_close_msg:nn { LaTeX / xparse } { not-single-char     }
\@@_close_msg:nn { fontspec       } { defining-font       }
\@@_close_msg:nn { fontspec       } { no-scripts          }
\@@_close_msg:nn { fontspec       } { set-scale           }
\@@_close_msg:nn { unicode-math   } { patch-macro         }
\ctex_at_end_package:nn { geometry } { \def\Gm@showparams#1{} }

\LoadClass{article}
\RequirePackage{amsmath,unicode-math,physics,geometry,ctexheading}

\geometry{hmargin=1cm, vmargin=2cm, showframe}
\unimathsetup{math-style=ISO, bold-style=ISO, mathrm=sym}
\ctexset{section/format+=\centering, subsection/format+=\centering}

\tl_new:N     \g_@@_font_tl
\clist_new:N  \g_@@_fira_weights_clist
\clist_new:N  \g_@@_xits_weights_clist
\clist_new:N  \g_@@_lm_weights_clist
\clist_set:Nn \g_@@_lm_weights_clist { 0 }  % Just a placeholder

\cs_new_protected:Npn \@@_set_fira_font:
  {
    \clist_map_inline:Nn \g_@@_fira_weights_clist
      { \setmathfont { FiraMath-##1.otf } [ Path = ../release/fonts/, version = ##1 ] }
  }
\cs_new_protected:Npn \@@_set_xits_font:
  {
    \clist_map_inline:Nn \g_@@_xits_weights_clist
      { \setmathfont { XITSMath-##1.otf } [ version = ##1 ] }
  }
\cs_new_protected:Npn \@@_set_lm_font:
  {
    \clist_map_inline:Nn \g_@@_xits_weights_clist
      { \setmathfont { latinmodern-math.otf } }
    \cs_set_eq:NN \mathversion \use_none:n
  }
\cs_new_protected:Npn \@@_test:n #1
  {
    \clist_map_inline:cn { g_@@_ \g_@@_font_tl _weights_clist }
      {
        \group_begin:
          \mathversion {##1} #1
        \group_end:
      }
  }
\NewDocumentCommand \Test { m }
  { \@@_test:n {#1} }

\keys_define:nn { fira-test }
  {
    % font = fira/xits/lm
    font .choices:nn =
      { fira, xits, lm }
      { \tl_set_eq:NN \g_@@_font_tl \l_keys_choice_tl },
    font .initial:n = fira,
    % weights = all/master/<weight>
    weights .code:n =
      {
        \tl_if_eq:nnTF {#1} { all }
          {
            \clist_gset:Nn \g_@@_fira_weights_clist
              {
                Thin, UltraLight, ExtraLight, Light, Book, Regular,
                Medium, SemiBold, Bold, ExtraBold, Heavy, Ultra
              }
            \clist_gset:Nn \g_@@_xits_weights_clist { Regular, Bold }
          }
          {
            \tl_if_eq:nnTF {#1} { master }
              {
                \clist_gset:Nn \g_@@_fira_weights_clist { Thin, Regular, Ultra }
                \clist_gset:Nn \g_@@_xits_weights_clist { Regular, Bold }
              }
              {
                \clist_gset:Nn \g_@@_fira_weights_clist {#1}
                \clist_gset:Nn \g_@@_xits_weights_clist {#1}
              }
          }
      },
    weights .initial:n = all
  }
\NewDocumentCommand \FiraTestSetup { m }
  { \keys_set:nn { fira-test } {#1} }

\ctex_at_end_preamble:n
  { \use:c { @@_set_ \g_@@_font_tl _font: } }

\endinput
