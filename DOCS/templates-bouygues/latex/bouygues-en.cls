%******************************************************************************%
%                                                                              %
%                            bouygues-en.cls                                   %
%                            Made by:                                           %
%                                Eugène NGONTANG                               %
%                                                                              %
%******************************************************************************%


\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{bouygues-en}[2012/16/01 v1.0
  LaTeX class for Bouygues-themed documents - English language]

\DeclareOption*{%
  % Pass every unknown option to the article class
  \PassOptionsToClass{\CurrentOption}{bouygues}
}
\ProcessOptions\relax
\LoadClass[]{bouygues}

\usepackage[english]{babel}