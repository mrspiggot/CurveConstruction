import pandas as pd

# dfs = pd.read_html("https://www.global-rates.com/en/interest-rates/euribor/euribor.aspx")
#
# print(type(dfs))
#
# i=0
# for df in dfs:
#     print("Start table ", i)
#     print(df.info())
#     print(df)
#     print("End table", i)
#     i+=1
#
# print(dfs[9].iloc[1,1])
# print(dfs[9].iloc[4,1])
# print(dfs[9].iloc[6,1])
# print(dfs[9].iloc[9,1])
# print(dfs[9].iloc[15,1])
# print(dfs[9].iloc[15,2])
#
#
# import pandas as pd
#
# dfs = pd.read_html("https://www.global-rates.com/en/interest-rates/libor/european-euro/euro.aspx")
#
# print(type(dfs))
#
# i=0
# for df in dfs:
#     print("Start table ", i)
#     print(df.info())
#     print(df)
#     print("End table", i)
#     i+=1
#
# print(dfs[9].iloc[1,1])
# print(dfs[9].iloc[2,1])
# print(dfs[9].iloc[4,1])
# print(dfs[9].iloc[5,1])
# print(dfs[9].iloc[6,1])
# print(dfs[9].iloc[9,2])
# print(dfs[9].iloc[15,2])

dfs = pd.read_html("https://www.lch.com/services/swapclear/essentials/settlement-prices")
i=0
for df in dfs:
    print("Start table ", i)
    print(df.info())
    print(df)
    print("End table", i)
    i+=1

TABLE = 0

print(dfs[TABLE].iloc[0,0], " ", dfs[TABLE].iloc[0,1])
print(dfs[TABLE].iloc[1,0], " ", dfs[TABLE].iloc[1,1])
print(dfs[TABLE].iloc[2,0], " ", dfs[TABLE].iloc[2,1])
print(dfs[TABLE].iloc[3,0], " ", dfs[TABLE].iloc[3,1])
print(dfs[TABLE].iloc[4,0], " ", dfs[TABLE].iloc[4,1])


print(type(dfs[3].iloc[0,1]))