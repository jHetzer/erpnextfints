SELECT
  PaymentName,
  SaleName,
  CustomerName,
  PaymentPostingDate
FROM
  (
    SELECT
      tpe.`name` AS PaymentName,
      tsi.`name` AS SaleName,
      tpe.`party_name` AS CustomerName,
      tsi.`outstanding_amount` AS Outstanding,
      tpe.`unallocated_amount` AS Amount,
      tsi.`posting_date` AS SalePostingDate,
      tsi.`due_date` AS SalesDueDate,
      tpe.`posting_date` AS PaymentPostingDate,
      REPLACE(
        tpe.`remarks`,
        CHAR(13),
        '<br>'
      ) AS Remarks,
      sum(tpe.`unallocated_amount`) OVER (PARTITION BY tsi.`name`) AS TotalAmount,
      count(*) OVER (PARTITION BY tpe.`name`) AS PaymentCount,
      count(*) OVER (PARTITION BY tsi.`name`) AS SalesCount
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
      ) AS tsi ON
      tsi.`posting_date` - INTERVAL tsi.`advanced_payment_days` DAY <= tpe.`posting_date`
      AND tsi.`due_date` >= tpe.`posting_date`
      AND tsi.`customer` = tpe.`party`
    WHERE
      tpe.`docstatus` = 0
      AND tpe.`payment_type` = 'Receive'
      AND tsi.`docstatus` = 1
      AND tsi.`outstanding_amount` > 0
    ORDER BY
      tpe.`name` ASC
  ) AS matches
WHERE
  `PaymentCount` = 1
  AND `TotalAmount` = `Outstanding`
