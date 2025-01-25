## What is this? 

These are the eth colors, that could be used to standardize plots across PBL in order to keep them consistent with the ETH color palette. 
The palette was taken from [here](https://ethz.ch/staffnet/en/service/communication/corporate-design/colours.html)

For the available colors you can check the website linked above, or [the source code](./src/eth_colors_pbl/eth_colors_pbl.py)

## Installation
```bash
git clone git@git.ee.ethz.ch:pbl/pbl-templates/eth-colors.git ~/eth-colors
cd ~/eth-colors
pip install .
```

## Usage 
```python
from eth_colors_pbl import ETHColors

...

plt.plot(x, y, color=ETHColors.ETH_BLUE)
```

A working example can be found [here](https://git.ee.ethz.ch/pbl/research/f1tenth/paperplots/rlpp-plots/-/commit/fe63d1c948e0480f56c7c46b3c63850280329fa5)

## License
no, it's PBL internal

## Contributing
If you think any function needs to be added, integrate it or create an issue

