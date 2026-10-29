# virtual_langloc

[TRIBEv2_langloc.ipynb](/TRIBEv2_langloc.ipynb) uses [TRIBEv2](https://arxiv.org/abs/2605.04326) to predict brain responses to sentences (S) and word lists (WL). The code is robust to additional conditions, so long as you provide an appropriately formatted stimulus file (see [stimuli.csv](/stimuli.csv) for an example). Basically, you need on column named `"stimulus"` and another column named `"condition"`. The condition can only be two-levels. The code handles the rest!

To open in Google Colab, click the button. 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/w-decker/virtual_langloc/blob/main/TRIBEv2_langloc.ipynb)