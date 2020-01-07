SELECT
  tPE.*
FROM
  `tabPayment Entry` AS tPE
WHERE
  -- Check "Bank Account" iban does not exist
  NOT EXISTS (
    SELECT
      1
    FROM
      `tabBank Account` AS tBA
    WHERE
      tBA.iban = tPE.iban
  )
  AND NOT EXISTS (
    -- Check "Payment Entry" is not a default customer/supplier
    SELECT
      1
    FROM
      `tabFinTS Login` AS tFL
    WHERE
      tFL.default_customer = tPE.party
      OR tFL.default_supplier = tPE.party
  )
  AND tPE.docstatus != 2
  -- Check requeried information are available
  AND tPE.party IS NOT NULL
  AND tPE.iban IS NOT NULL
  AND tPE.sender IS NOT NULL
  -- Only german banks are supported
  AND tPE.iban LIKE 'DE%'
GROUP BY
  -- Remove duplicate entires
  tPE.iban,
  tPE.party,
  tPE.sender
ORDER BY
  tPE.party;
