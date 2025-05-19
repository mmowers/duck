import pandas as pd
import os

#Switches
peak_load = 100 #MW
peak_price = 100 #$/MWh
pv_max_cap = 400 #MW
pv_steps = 20 #total number of steps

this_dir = os.path.dirname(os.path.abspath(__file__))
#Read input csv, which has these columns: hour, cf_pv, cf_load

df_in = pd.read_csv(f'{this_dir}/cf.csv')
df_in['load'] = peak_load * df_in['cf_load']

ls_df_hr = []
ls_df_sum = []
for i in range(1, pv_steps + 1):
    df = df_in.copy()
    pv_cap = pv_max_cap * i / pv_steps
    df.insert(loc=0, column='pv_cap', value=pv_cap)
    df['maxgen_pv'] = df['cf_pv'] * pv_cap
    df['gen_pv'] = df[['load', 'maxgen_pv']].min(axis=1)
    df['gen_other'] = df['load'] - df['gen_pv']
    df['curt_pv'] = df['maxgen_pv'] - df['gen_pv']
    df['price_load'] = df['gen_other'] / peak_load * peak_price #Just assuming linear relationship between gen_other and price
    ls_df_hr.append(df)
    market_share_pv = df['gen_pv'].sum() / df['load'].sum()
    lvoe_pv = (df['gen_pv']*df['price_load']).sum()/(df['gen_pv'].sum())
    lvoe_pv_uncurt = (df['maxgen_pv']*df['price_load']).sum()/(df['maxgen_pv'].sum())
    price_ave = (df['load']*df['price_load']).sum()/(df['load'].sum()) #load-weighted average
    value_factor_pv = lvoe_pv / price_ave
    value_factor_pv_uncurt = lvoe_pv_uncurt / price_ave
    integration_cost_pv = price_ave - lvoe_pv
    integration_cost_pv_uncurt = price_ave - lvoe_pv_uncurt
    ls_df_sum.append({'pv_cap':pv_cap, 'market_share_pv':market_share_pv, 'lvoe_pv':lvoe_pv, 'price_ave':price_ave, 'value_factor_pv':value_factor_pv, 'value_factor_pv_uncurt':value_factor_pv_uncurt, 'integration_cost_pv':integration_cost_pv, 'integration_cost_pv_uncurt':integration_cost_pv_uncurt})
df_hr = pd.concat(ls_df_hr, ignore_index=True)
df_sum = pd.DataFrame(ls_df_sum)
df_hr.to_csv(f'{this_dir}/df_hr.csv', index=False)
df_sum.to_csv(f'{this_dir}/df_sum.csv', index=False)