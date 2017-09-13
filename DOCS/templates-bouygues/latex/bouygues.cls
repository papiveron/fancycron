%******************************************************************************%
%                                                                              %
%                            bouygues.cls                                      %
%                            Made by:                                          %
%                                Eugène NGONTANG                               %
%                                                                              %
%******************************************************************************%

%
% This class specializes the ultimaade-common class to include features
% used by Ultimaade
%
% This class is organized this way :
%
% I - General LaTeX boilerplate
% II - Custom logo
% III - Custom Bouygues documents
%  1 - Custom fieds for tables
%  2 - Custom tables for templates


%%
%% I - General LaTeX boilerplate
%%

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{bouygues}[2010/07/15 v2.0
  LaTeX class for Bouygues-themed documents]

\DeclareOption*{%
  % Pass every unknown option to the epitech-common class
  \PassOptionsToClass{\CurrentOption}{bouygues-common}
}
\ProcessOptions\relax
\LoadClass[]{bouygues-common}

%%
%% II - Custom logo
%%

\newcommand{\bouygueslogo}[1]{\def \@bouygueslogo {#1}}
%%\ultimaadelogo{ultimaade_logo.png}
\bouygueslogo{bouygues_logo.pdf}
%%\ultimaadelogo{ultimaade_minilogo.pdf}

%%
%% III - Custom tables for Bouygues documents
%%

%% III.1 - Custom fields for tables

\makeatletter
\newcommand{\turnindir}[1]{\def \@turnindir {#1}}

\newcommand{\daypiscine}[1]{\def \@daypiscine {#1}}

\newcommand{\extitle}[1]{\def \@extitle {#1}}

\newcommand{\exnumber}[1]{\def \@exnumber {#1}}

\newcommand{\exscore}[1]{\def \@exscore {#1}}

\newcommand{\exflags}[1][-W -Wall -Werror]{\def \@exflags {#1}}

\newcommand{\excompil}[1][g++]{\def \@excompil {#1}}

\newcommand{\exmake}[1][Non]{\def \@exmake {#1}}

\newcommand{\exrules}[1][n/a]{\def \@exrules {#1}}

\newcommand{\exfiles}[1]{\def \@exfiles {#1}}

\newcommand{\exnotes}[1][n/a]{\def \@exnotes {#1}}

\newcommand{\exforbidden}[1][Aucune]{\def \@exforbidden {#1}}



%% III.2 - Custom tables for templates



\newcommand{\makeheader}
{
  \begin{tabularx}{\textwidth}{|X X  X X|}
    \hline
  \multicolumn{1}{|>{\raggedright}m{1cm}|}
              {\includegraphics[height=1cm]{\@bouygueslogo}} & 
  \multicolumn{2}{>{\centering}m{12cm}}{\small Exercice : \@exnumber } &
  \multicolumn{1}{ >{\raggedleft}p{1.5cm}|} 
              {\scriptsize points : \@exscore} \\ \hline

  \multicolumn{4}{|>{\centering}m{15cm}|}
              {\small \@extitle} \\ \hline

  \multicolumn{4}{|>{\raggedright}m{15cm}|}
              {\small R\'{e}pertoire de rendu: \ttfamily 
                \@turnindir/ex\@exnumber }
              \\ \hline

  \multicolumn{2}{|>{\raggedright}m{7.5cm}}
              {\small Compilateur : \ttfamily \@excompil } & 
  \multicolumn{2}{|>{\raggedright}m{7.5cm}|}
              {\small Flags de compilation: 
                \ttfamily \@exflags }
              \\ \hline

  \multicolumn{2}{|>{\raggedright}m{7.52cm}}
              {\small Makefile : \ttfamily{\@exmake}} &  
  \multicolumn{2}{|>{\raggedright}m{7.5cm}|}
              {R\`{e}gles : \ttfamily \@exrules } \\ \hline

  \multicolumn{4}{|>{\raggedright}m{15cm}|}
              {\small Fichiers a rendre : \ttfamily \@exfiles }
              \\ \hline
                    
   \multicolumn{4}{|>{\raggedright}m{15cm}|}
               {\small Remarques : \ttfamily \@exnotes } 
               \\ \hline

   \multicolumn{4}{|>{\raggedright}m{15cm}|}
               {\small Fonctions Interdites : \ttfamily \@exforbidden } 
               \\ \hline
\end{tabularx}
\exnotes
\exrules
\exmake
\exforbidden
\extitle{}
\exnumber{}
}
