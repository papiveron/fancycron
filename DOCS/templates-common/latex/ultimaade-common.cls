%******************************************************************************%
%                                                                              %
%                           ultimaade-common.cls                               %
%                           Made by:                                           %
%                                Eugène NGONTANG <ngonta_e@epitech.net>        %
%                                                                              %
%******************************************************************************%

%
% This class provides a layout for teaching material in Ultimaade.
% This class only contains the common layout and features. More specialized
% features will be implemented by subclasses.
%
% This is version 2 of this class.
%
% This class is organized this way :
%
% I - Documentation
%  1. Incompatibilites
% II - General LaTeX boilerplate
%  1. Definition
%  2. Class options and parent class
%  3. Imports
% III - Lengths and color redefinitions
%  1. Lenghts
%  2. Colors
%  3. Hyperlinks
%  4. Listings
%  5. Page layout
%  6. Roman numerals for chapters
% IV - Frontpage customization
%  1. Custom fields
%  2. Redefinition of \maketitle
% V - Custom helper commands
%  1. Hint/warn
%  2. Lisibility helper

%%
%% I - Documentation
%%

%% I.1 - Incompatibilities

% Package ulem:
% The package ulem has a lot of oddities. Using it is not always a
% good idea. If you really want to do so, you should import it with
% the [normalem] option, as such :
%   \usepackage[normalem]{ulem}
% Otherwise, it overrides \emph to underline the emphasized text. So
% far so good, but underlined text is typesetted in a box, which means
% that linebreaks don't happen automatically. Since \abstract (among
% others) uses \emph, the abstract is unreadable by default.
% Please read thoroughly ulem's doc before using it.
% See also: http://www.tex.ac.uk/cgi-bin/texfaq2html?label=underline

%%
%% II - General LaTeX boilerplate
%%

%% II.1 - Definition

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{ultimaade-common}[2010/07/15 v2.0
  LaTeX class for Ultimaade-themed documents]

%% II.2 - Class options and parent class

\newcommand{\summarytitle}{Abstract}
\DeclareOption{fr}{%
  \renewcommand{\summarytitle}{R\'esum\'e}%
}

\DeclareOption*{%
  \PassOptionsToClass{\CurrentOption}{report}
}

\ProcessOptions\relax
\LoadClass[a4paper,12pt,onecolumn]{report}

%% II.3 - Imports

\usepackage[top=1in,bottom=1in,left=1in,right=1in]{geometry}
\usepackage[pdftex]{graphicx}
\usepackage{url}
\usepackage{fancyhdr}
\usepackage{array}
\usepackage[table]{xcolor}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{listings}
\usepackage{tabularx}
\usepackage{color}
\usepackage[pdftex]{hyperref}
\usepackage{fancybox}
\usepackage{float}
\usepackage{atbeginend} % provided locally : atbeginend.sty
\usepackage{tocloft} % provided locally : tocloft.sty
\usepackage{multirow} % provided locally : multirow.sty

%% III - Lengths and color redefinitions

%% III.1 - Lengths

\AfterBegin{enumerate}{
  \itemsep10pt%
}
\AfterBegin{itemize}{
  \itemsep10pt%
  \renewcommand{\labelitemi}{$\bullet$}%
  \renewcommand{\labelitemii}{$\circ$}%
}

\BeforeBegin{enumerate}{\vspace{15pt}}
\AfterEnd{enumerate}{\vspace{15pt}}

\BeforeBegin{itemize}{\vspace{15pt}}
\AfterEnd{itemize}{\vspace{15pt}}

\BeforeBegin{lstlisting}{\vspace{15pt}}
\AfterEnd{lstlisting}{\vspace{15pt}}

\BeforeBegin{tabularx}{\vspace{15pt}}
\AfterEnd{tabularx}{\vspace{15pt}}

%% III.2 - Colors

\definecolor{nicergreen}{rgb}{0,0.502,0}
\definecolor{nicerblue}{rgb}{0,0.302,1}
\definecolor{nicerorange}{rgb}{1,0.502,0}
\definecolor{nicergrey}{rgb}{0.502,0.502,0.502}
\definecolor{nicerred}{rgb}{0.626,0,0}
\definecolor{hintbg}{rgb}{1.0,1.0,0.75}
\definecolor{warnbg}{rgb}{1.0,0.75,0.75}
\definecolor{infobg}{rgb}{0.75,0.75,1.0}
\definecolor{bibliotechbg}{RGB}{239,253,255}

%% III.3 - Hyperlinks

\hypersetup
{
  colorlinks,
%  citecolor=black,                %
%  filecolor=black,                %
  linkcolor=black,                % black links
  urlcolor=blue                   % blue URLs
}

%% III.4 - Listings

\lstset
{
  backgroundcolor=\color{gray!15},
  basicstyle=\small\ttfamily,
  breaklines=true,
  columns=fullflexible,
  frame=lines,
  tabsize=4,
  numbers=left,
  numberstyle=\scriptsize\ttfamily,
  numbersep=5pt,
  showspaces=false,
  showstringspaces=false,
  showtabs=false,
  breaklines=true,
  float
}

%% III.5 - Page layout

\makeatletter
\pagestyle{fancy}
\lhead{\@title}
\rhead{\@subtitle}
\cfoot{\thepage}
\makeatother

%% III.6 - Roman chapter style

% custom sections style

\renewcommand{\thechapter}{\Roman{chapter}}

% Using  roman  numerals  makes  the  TOC  section/subsection  numbers
% overflow on the  right. This adds some margin to  avoid that kind of
% problems. (requires \usepackage{tocloft})
\setlength{\cftchapnumwidth}{1cm}
\setlength{\cftsecnumwidth}{1.5cm}
\setlength{\cftsubsecnumwidth}{1.3cm}
\setlength{\cftsubsubsecnumwidth}{1.6cm}


%% IV - Frontpage customization

%% IV.1 - Custom fields
\makeatletter
\newcommand{\website}[1]{\def \@website {#1}}
\website{}

\newcommand{\subtitle}[1]{\def \@subtitle {#1}}
\subtitle{}

\newcommand{\schoollogo}[1]{\def \@schoollogo {#1}}
\schoollogo{epitech_logo.pdf}

\newcommand{\summary}[1]{\def \@summary {#1}}
\summary{}

\edef\@authors{}
\newcommand{\member}[2]{%
  \protected@edef\@authors{\@authors #1 \protect\url{#2}\\}
  \author{\@authors}
}
\author{}

%% IV.2 - Redefine \maketitle

\makeatletter
\def \maketitle {
   \begin{titlepage}
    \begin{center}

      
      \includegraphics[height=3cm]{\@ultimaadelogo}
      \vskip 3em
      {\huge \@title}
      \vskip 2em
      {\LARGE \@subtitle}
      \vskip 5em
    \end{center}
    \begin{center}
	  \@author
    \end{center}
	\vskip 3em
    \emph{\underline{\textbf{\summarytitle}} : \@summary}
  \end{titlepage}
}
\makeatother

\fancyput(-2.54cm,-27.16cm){\includegraphics[width=21cm,height=29.7cm]{back-ultimaade-NB.pdf}}

%% V - Custom helper commands

%% V.1 - Hint/Warn

% hint command

\newcommand{\kbox}[3]
{
  \vskip 15pt
  \noindent
  \colorbox{#1}
  {
    \begin{tabular*}{\textwidth}{m{4em}m{0.8\textwidth}}
        \includegraphics[width=4em]{#2}
      & {\ttfamily\footnotesize #3}\\
    \end{tabular*}
  }
  \vskip 15pt
}

\newcommand{\hint}[1]{\kbox{hintbg}{helphint.pdf}{#1}}
\newcommand{\warn}[1]{\kbox{warnbg}{warn.pdf}{#1}}
\newcommand{\info}[1]{\kbox{infobg}{info.pdf}{#1}}
%%u\newcommand{\bibliotech}[1]{\kbox{bibliotechbg}{bibliotech_minilogo.png}{#1}}

%% V.2 Lisibility helper

\makeatletter
\newcommand{\mso}[1]{
  \ttfamily #1 \normalfont
}