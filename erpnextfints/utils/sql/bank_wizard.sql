SELECT
  tPE.*
FROM
  `tabPayment Entry` AS tPE
  LEFT JOIN `tabBank Account` AS tBA ON tPE.iban = tBA.iban
  AND tPE.sender = tBA.account_name
  LEFT JOIN `tabFinTS Login` as tFL ON tPE.party = tFL.default_customer
  or tPE.party = tFL.default_supplier
WHERE
  tFL.name IS NULL
  AND tBA.name IS NULL
  AND tPE.docstatus != 2
  AND tPE.party IS NOT NULL
  AND tPE.iban IS NOT NULL
  AND tPE.iban LIKE 'DE%'
  AND tPE.sender IS NOT NULL
GROUP BY
  iban,
  sender
HAVING
  COUNT(tPE.iban) = 1;
