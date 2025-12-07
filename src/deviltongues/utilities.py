import refinitiv.data as rd
from refinitiv.data.discovery import Chain
from refinitiv.data.content import search
import pandas as pd
from datetime import datetime

# Step 1: Open session
rd.open_session()

strikes_and_expiries=rd.discovery.search(
	view = rd.discovery.Views.EQUITY_QUOTES,
	query = "tsla",
	top = 10,
	filter = "( SearchAllCategoryv2 eq 'Options' and (ExpiryDate gt 2025-12-06 and ExpiryDate lt 2026-01-31 and (StrikePrice ge 300 and StrikePrice le 500) and ExchangeName xeq 'OPRA' and (UnderlyingQuoteRIC eq 'TSLA.O')))",
	select = "DTSubjectName,AssetState,BusinessEntity,PI,SearchAllCategoryv3,SearchAllCategoryv2,SearchAllCategory,ExchangeName,CallPutOption,StrikePrice,ExpiryDate,RIC,UnderlyingQuoteRIC,UnderlyingIssuerName,ExchangeCode,UnderlyingRCSAssetCategoryLeaf"
)

print(strikes_and_expiries)


# # Step 2: Get underlying spot
# underlying_ric = "TSLA.O"
# spot_df = rd.get_data(underlying_ric, ['TR.PriceClose'])
# spot = spot_df['Price Close'].iloc[0]
# print(f"TSLA spot: {spot:.2f}")
#
#
#
# strikes_and_expiries=rd.discovery.search(
# 	view = rd.discovery.Views.EQUITY_QUOTES,
# 	query = "tsla",
# 	top = 10,
# 	filter = "( SearchAllCategoryv2 eq 'Options' and (ExpiryDate gt 2025-12-06 and ExpiryDate lt 2026-01-31 and (StrikePrice ge 300 and StrikePrice le 500) and ExchangeName xeq 'OPRA' and (UnderlyingQuoteRIC eq 'TSLA.O')))",
# 	select = "DTSubjectName,AssetState,BusinessEntity,PI,SearchAllCategoryv3,SearchAllCategoryv2,SearchAllCategory,ExchangeName,CallPutOption,StrikePrice,ExpiryDate,RIC,UnderlyingQuoteRIC,UnderlyingIssuerName,ExchangeCode,UnderlyingRCSAssetCategoryLeaf"
# )
#
# rd.get_data(
#     universe = list(strikes_and_expiries['RIC']),
#     fields = ['TR.PriceClose']
# )

rd.close_session()