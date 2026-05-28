# PURPOSE:
# INPUTS:
# OUTPUTS:
# SIDE EFFECTS:
# FAILURE MODES:

import os

TEST_DB = os.getenv("TEST_DB", "sqlite:///test.db")
PROD_DB = os.getenv("PROD_DB", "sqlite:///opexio.db")


