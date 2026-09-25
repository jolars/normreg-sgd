\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{alt2027}[2026/08/30 v1.0 ALT 2027 Proceedings]
% Track whether a font size (10/11/12pt) was explicitly requested
\newif\ifaltSizeOption
\altSizeOptionfalse
% Temporary environment for proofs of named results.
\newenvironment{proofof}[1]{\begin{proof}\textbf{of {#1}}}{\end{proof}}

\@ifundefined{ifanonsubmission}{
  \newif\ifanonsubmission
  \anonsubmissionfalse
}{}

\@ifundefined{iffinalsubmission}{
  \newif\iffinalsubmission
  \finalsubmissionfalse
}{}

\DeclareOption{anon}{\anonsubmissiontrue}
\DeclareOption{final}{\finalsubmissiontrue}
% Font sizes were not previously passed correctly to jmlr.cls, which
% means the sample file's "12pt" was ignored and reverted to "11pt".
% Therefore we add the parameters but default to 11pt.
%
% Forward font size options to jmlr so 12pt/10pt work
\DeclareOption{10pt}{\altSizeOptiontrue\PassOptionsToClass{10pt}{jmlr}}
\DeclareOption{11pt}{\altSizeOptiontrue\PassOptionsToClass{11pt}{jmlr}}
\DeclareOption{12pt}{\altSizeOptiontrue\PassOptionsToClass{12pt}{jmlr}}
\ProcessOptions\relax
% If no size option was given, default explicitly to 11pt
\ifaltSizeOption\else\PassOptionsToClass{11pt}{jmlr}\fi

\LoadClass[pmlr]{jmlr}

% Replace TBD with the assigned PMLR volume before publishing camera-ready papers.
\jmlrvolume{vol {TBD}}
\jmlryear{2027}
\jmlrproceedings{PMLR}{Proceedings of Machine Learning Research}

\ifanonsubmission
 \newcommand{\altauthor}[1]{}
 \author{author names withheld}
 \editor{Under Review for ALT 2027}
 \jmlrworkshop{38th International Conference on Algorithmic Learning Theory}
 \renewcommand{\acks}[1]{}
\else
 \newcommand{\altauthor}[1]{\author{#1}}
 \iffinalsubmission
 \editors{Surbhi Goel and Nikita Zhivotovskiy}
 \jmlrworkshop{38th International Conference on Algorithmic Learning Theory}
 \fi
\fi
