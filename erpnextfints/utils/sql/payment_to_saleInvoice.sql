SELECT
  PaymentName,
  SaleName,
  CustomerName,
  PaymentPostingDate
FROM
  (
    SELECT
      tpe.`NAME` AS PaymentName,
      tpe.`party_name` AS CustomerName,
      tpe.`posting_date` AS PaymentPostingDate,
      tpe.`unallocated_amount` AS Amount,
      tsi.`NAME` AS SaleName,
      tsi.`posting_date` AS SalePostingDate,
      tsi.`due_date` AS SalesDueDate,
      replace(
        tpe.`remarks`,
        char(13),
        '<br>'
      ) AS remarks,
      count(*) OVER (PARTITION BY tpe.`NAME`) AS PaymentCount,
      count(*) OVER (PARTITION BY tsi.`NAME`) AS SalesCount
    FROM
      `tabPayment Entry` AS tpe
      LEFT JOIN (
        SELECT
          tsi.`NAME`,
          tsi.`posting_date`,
          tsi.`due_date`,
          tsi.`outstanding_amount`,
          tsi.`customer`,
          tsi.`docstatus`,
          tcus.`advanced_payment_days`
        FROM
          `tabSales Invoice` AS tsi
          LEFT JOIN `tabCustomer` AS tcus ON tsi.`customer` = tcus.`NAME`
      ) AS tsi ON tsi.`outstanding_amount` = tpe.`unallocated_amount`
      AND tsi.`posting_date` - INTERVAL tsi.`advanced_payment_days` DAY <= tpe.`posting_date`
      AND tsi.`due_date` >= tpe.`posting_date`
      AND tsi.`customer` = tpe.`party`
    WHERE
      tpe.`docstatus` = 0
      AND tpe.`payment_type` = 'Receive'
      AND tsi.`docstatus` = 1
      AND tsi.`outstanding_amount` > 0
    ORDER BY
      tpe.`NAME` ASC
) AS matches
WHERE
  `PaymentCount` = 1
  AND `SalesCount` = 1
