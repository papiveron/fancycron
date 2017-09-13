%******************************************************************************%
%                                                                              %
%                            bouygues-fr.cls                                   %
%                            Made by:                                           %
%                                Eugène NGONTANG                               %
%                                                                              %
%******************************************************************************%


\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{bouygues-fr}[2012/01/16 v1.0
  LaTeX class for Bouygues-themed documents - French language]

\DeclareOption*{%
  % Pass every unknown option to the article class
  \PassOptionsToClass{\CurrentOption}{bouygues}
}
\ProcessOptions\relax
\LoadClass[fr]{bouygues}

\usepackage[french]{babel}
