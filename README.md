# logseq-export-page-from-journals
export from journals all blocks that reference PAGE. Output in date order, retaining original markdown.  

logseqPageExport searches all Journals for blocks referencing the provided <tag_or_page_name>. Outputs the date of each Journal that contained matching block(s), followed by the matched block(s). Output is similar to clicking a PageName in LogSeq, but with the following benefits: 
- output is chronological, rather than reverse-chronological.
- output is a markdown file containing only the target blocks that may be opened in any editor.
- single operation, whereas a copy&paste from a page when the selection spans multiple journal dates, the journal dates are dropped from the pasted output.

Especially useful when a Page is referenced by blocks within many different Journal files, and same Journal files also contain blocks referencing other Pages. logseqPageExport gives us only the matching blocks from all journals.
