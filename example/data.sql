with decisions as (
  select
    txn_id,
    accounts_id,
    max(case when decision = 'Fraud' then 1 else 0 end) as is_fraud,
    max(case when decision = 'Legitimate' then 1 else 0 end) as is_legitimate,
    max(is_false_positive) as is_false_positive,
    max(created_at) as max_created_at,
    min(created_at) as min_created_at,
    count(*) as total_decisions
  from
    fraud_decisions
  group by
    txn_id,
    accounts_id
),
txns as (
select
  txn.id as txn_id,
  txn.accounts_id,
  accts.organization_id as org_id,
  txn.created_at as txn_created_at,
   txn.settled_at as txn_settled_at,
   strftime('%H', txn.created_at)::int as txn_created_at_hr,
   (julian(txn.settled_at) - julian(txn.created_at))*24*60 as settlement_time_mins,
   (julian(txn.created_at) - julian(accts.created_at)) as acct_tenure_days,
   (julian(txn.created_at) - julian(org.created_at)) as org_tenure_days,
  txn.status as txn_status,
  txn.amount as txn_amount,
  substr(cast(txn.amount as text), instr(cast(txn.amount as text), '.') - 1, 1)::int as benford_ones_digit,
  case
    when txn.amount > 0 then 'credit'
    when txn.amount < 0 then 'debit'
  end as txn_type,
  accts.account_type,
  accts.created_at as accts_created_at,
  accts.is_closed as accts_is_closed,
  org.website as org_website,
  case
    when org.website is not null then 1 else 0
  end as org_has_website,
  org.created_at as org_created_at,
  org.is_active as org_is_active,
  org.country as org_country,
  case when org.industry is null then 'industry unavailable' else org.industry end as org_industry,
from
  transactions as txn
left join decisions on txn.id = decisions.txn_id and txn.accounts_id = decisions.accounts_id
left join accounts as accts on txn.accounts_id = accts.id
left join organizations as org on accts.organization_id = org.id


),
usr as (
  select
    u.organization_id,
    txn_inner.txn_created_at as txn_date,
    count(distinct case when u.created_at < txn_inner.txn_created_at then u.id end) as org_num_users,
    count(distinct case when u.is_primary_user = 1 and u.created_at < txn_inner.txn_created_at then u.id end) as org_num_primary_users,
    count(distinct case when u.email is not null and u.created_at < txn_inner.txn_created_at then u.id end) as org_num_users_with_email,
    org_num_users_with_email/nullif(org_num_users,0) as ratio_users_with_email,
    count(distinct case when u.created_at >= (txn_inner.txn_created_at) - interval '1 day'
                        and u.created_at < (txn_inner.txn_created_at) then u.id end) as users_added_previous_day
  from
    users u
  join txns txn_inner on u.organization_id = txn_inner.org_id
  group by
    u.organization_id, txn_inner.txn_created_at
),
txn_velocity as (
  select
    org_id,
    txn_created_at as txn_date,
    count(*) over (partition by org_id order by txn_created_at range between interval '30 days' preceding and interval '1 second' preceding) as txn_count_30d,
    avg(txn_amount) over (partition by org_id order by txn_created_at range between interval '30 days' preceding and interval '1 second' preceding) as avg_txn_amount_30d,
    sum(case when txn_amount > 5000 then 1 else 0 end) over (partition by org_id 
                                                        order by txn_created_at range between interval '30 days' preceding and interval '1 second' preceding) as high_value_txn_count_30d
  from
    txns

),
org_failure_rate as (
select
  org_id,
  txn_created_at as txn_date,
  sum(case when txn_status = 'failed' then 1 else 0 end) over w as failed_cnts,
  count(*) over w as total_cnts,
  1.0 * failed_cnts / nullif(total_cnts, 0) as failure_rate
from
  txns
window w as (
  partition by org_id
  order by txn_created_at 
  rows between unbounded preceding and 1 preceding
)


)

select
       txns.txn_id,
       txns.accounts_id,
       txns.org_id,
       txns.txn_created_at,
       txns.txn_settled_at,
       txns.txn_created_at_hr,
       txns.settlement_time_mins,
       txns.acct_tenure_days,
       txns.org_tenure_days,
       txns.txn_status,
       txns.txn_amount,
       txns.benford_ones_digit,
       txns.txn_type,
       txns.account_type,
       txns.accts_created_at,
       txns.accts_is_closed,
       txns.org_website,
       txns.org_has_website,
       txns.org_created_at,
       txns.org_is_active,
       txns.org_country,
       txns.org_industry,
       usr.org_num_users,
       usr.org_num_primary_users,
       usr.org_num_users_with_email,
       usr.ratio_users_with_email,
       usr.users_added_previous_day,
       txn_velocity.txn_count_30d,
       txn_velocity.avg_txn_amount_30d,
       txn_velocity.high_value_txn_count_30d,
       org_failure_rate.failure_rate as org_txn_failure_rate,
       decisions.is_fraud,
       decisions.is_legitimate,
       decisions.is_false_positive,
       decisions.max_created_at as frd_max_created_at,
       decisions.min_created_at as frd_min_created_at,
       decisions.total_decisions
from txns
left join usr on txns.org_id = usr.organization_id and usr.txn_date = txns.txn_created_at
left join txn_velocity on txn_velocity.org_id = txns.org_id and txn_velocity.txn_date = txns.txn_created_at
left join org_failure_rate on org_failure_rate.org_id = txns.org_id and org_failure_rate.txn_date = txns.txn_created_at
left join decisions on decisions.txn_id = txns.txn_id and decisions.accounts_id = txns.accounts_id
