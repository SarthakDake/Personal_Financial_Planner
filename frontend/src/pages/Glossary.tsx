import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const SECTIONS: Array<{
  title: string
  items: Array<{ term: string; meaning: string; tip?: string }>
}> = [
  {
    title: 'Cash Flow & Ratios',
    items: [
      {
        term: 'Net Worth',
        meaning: 'Total assets minus total liabilities. Your financial balance sheet snapshot.',
        tip: 'Track financial net worth (excluding primary home) separately for investment progress.',
      },
      {
        term: 'Monthly Surplus',
        meaning: 'Monthly income minus expenses, EMIs, and SIPs already committed.',
        tip: 'Positive surplus funds new goals; negative surplus needs expense or debt action.',
      },
      {
        term: 'Savings Ratio',
        meaning: 'Share of monthly income left after living expenses and EMIs (before optional SIPs).',
        tip: 'Target 20%+ for healthy wealth building.',
      },
      {
        term: 'DTI (Debt-to-Income)',
        meaning: 'Total monthly EMIs divided by monthly income.',
        tip: 'Keep under 40% for comfort; above 50% is stressed.',
      },
      {
        term: 'Emergency Fund',
        meaning: 'Liquid money set aside for job loss or medical shocks.',
        tip: 'Typically 3–12 months of essential expenses depending on risk profile.',
      },
    ],
  },
  {
    title: 'Investing & Returns',
    items: [
      {
        term: 'SIP',
        meaning: 'Systematic Investment Plan — fixed amount invested every month into mutual funds.',
        tip: 'Enter SIP as Monthly ₹ in the Investments tab.',
      },
      {
        term: 'Lumpsum',
        meaning: 'One-time investment of a large amount.',
        tip: 'Shown as Current Amount / Corpus in the Investments tab.',
      },
      {
        term: 'Expected Return (%)',
        meaning: 'Assumed annual growth rate used for projections.',
        tip: 'Enter 12 for 12% — never 0.12. All % fields use whole percentages.',
      },
      {
        term: 'CAGR',
        meaning: 'Compound Annual Growth Rate — smoothed yearly return between two values.',
      },
      {
        term: 'XIRR',
        meaning: 'Extended Internal Rate of Return for irregular cash flows (SIPs, redemptions).',
      },
      {
        term: 'Asset Allocation',
        meaning: 'Mix of equity, debt, gold, and other assets in the portfolio.',
        tip: 'Aligned to risk profile and age (equity often capped near 100 − age).',
      },
      {
        term: 'Rebalancing',
        meaning: 'Adjusting holdings back toward the target allocation after markets drift.',
      },
    ],
  },
  {
    title: 'Retirement & Independence',
    items: [
      {
        term: 'Retirement Corpus',
        meaning: 'Total wealth needed at retirement to fund living expenses for life expectancy.',
      },
      {
        term: 'SWR (Safe Withdrawal Rate)',
        meaning: 'Annual % of corpus you can withdraw with a high chance of sustainability.',
        tip: 'Common starting point is 4%. Enter as 4, not 0.04.',
      },
      {
        term: 'FIRE Number',
        meaning: 'Financial Independence corpus = annual expenses ÷ SWR.',
      },
      {
        term: 'Bucket Strategy',
        meaning: 'Split retirement money into short-term (cash/debt), medium (hybrid), and long-term (equity) buckets.',
      },
      {
        term: 'Monte Carlo Simulation',
        meaning: 'Thousands of random market-return paths to estimate the odds your corpus lasts.',
        tip: 'Success rate ≥ 85% is often treated as comfortable.',
      },
      {
        term: 'PPF / EPF / NPS',
        meaning:
          'PPF = Public Provident Fund; EPF = Employees’ Provident Fund; NPS = National Pension System — retirement-oriented savings with tax benefits.',
      },
    ],
  },
  {
    title: 'Loans',
    items: [
      {
        term: 'EMI',
        meaning: 'Equated Monthly Instalment — fixed monthly loan payment.',
        tip: 'Always enter as Monthly ₹.',
      },
      {
        term: 'Outstanding Principal',
        meaning: 'Amount still owed on the loan today (lump sum ₹).',
      },
      {
        term: 'Amortization Schedule',
        meaning: 'Month-by-month split of each EMI into interest and principal.',
      },
      {
        term: 'Prepayment',
        meaning: 'Extra lump-sum payment that reduces principal and usually interest/tenure.',
      },
      {
        term: 'Interest Rate (Annual %)',
        meaning: 'Yearly rate charged by the lender.',
        tip: 'Enter 8.5 for 8.5% p.a., not 0.085.',
      },
    ],
  },
  {
    title: 'Insurance & Protection',
    items: [
      {
        term: 'HLV (Human Life Value)',
        meaning: 'Present value of future earnings that dependents would lose if the earner dies.',
      },
      {
        term: 'Sum Assured / Cover',
        meaning: 'Payout amount from a life or health policy (₹ lump sum), not the premium.',
      },
      {
        term: 'Premium (Annual ₹)',
        meaning: 'Yearly cost of keeping the insurance policy active.',
      },
      {
        term: 'Critical Illness Cover',
        meaning: 'Lump-sum benefit on diagnosis of specified major illnesses.',
      },
    ],
  },
  {
    title: 'Tax (India)',
    items: [
      {
        term: 'Old vs New Regime',
        meaning: 'Two parallel income-tax systems. Old allows more deductions; New has lower slabs with fewer deductions.',
        tip: 'All tax amounts in the planner are Annual ₹.',
      },
      {
        term: 'Section 80C',
        meaning: 'Deduction up to ₹1.5L for EPF, PPF, ELSS, life premium, principal repayment, etc. (Old regime).',
      },
      {
        term: 'Section 80CCD(1B)',
        meaning: 'Additional ₹50,000 deduction for voluntary NPS contribution.',
      },
      {
        term: 'Section 80D',
        meaning: 'Deduction for health insurance premiums for self/family and parents.',
      },
      {
        term: 'HRA',
        meaning: 'House Rent Allowance exemption based on rent paid, salary, and metro/non-metro city.',
      },
      {
        term: 'LTCG / STCG',
        meaning: 'Long-Term / Short-Term Capital Gains on investments — taxed at special rates.',
      },
    ],
  },
  {
    title: 'Goals & Inflation',
    items: [
      {
        term: 'Current Cost',
        meaning: 'What the goal would cost if you bought it today (₹).',
      },
      {
        term: 'Future Cost',
        meaning: 'Inflation-adjusted cost on the target date.',
      },
      {
        term: 'Inflation (Annual %)',
        meaning: 'Assumed yearly rise in prices.',
        tip: 'Enter 6 for 6%. Education/healthcare often use higher rates.',
      },
      {
        term: 'Years from Now',
        meaning: 'In Goals, values under 100 are treated as years until the goal (e.g. 5 = five years).',
      },
    ],
  },
  {
    title: 'How to Enter Data in This App',
    items: [
      {
        term: 'Monthly vs Annual',
        meaning:
          'Every money field label states the period. Monthly fields end with (Monthly ₹). Annual fields end with (Annual ₹). Asset balances and covers are lump-sum ₹.',
      },
      {
        term: 'Percentages',
        meaning:
          'Interest rates, expected returns, inflation, and SWR are entered as normal percentages: 8.5 means 8.5%. Do not enter 0.085.',
      },
      {
        term: 'Risk Profile',
        meaning: 'Conservative / Moderate / Aggressive — drives suggested asset allocation and default returns.',
      },
      {
        term: 'What-If Analysis',
        meaning: 'Interactive sliders to stress-test income, expenses, SIP, inflation, returns, and retirement age.',
      },
    ],
  },
]

export default function Glossary() {
  return (
    <div className="space-y-6">
      <div className="animate-fade-up">
        <h1 className="font-display text-3xl sm:text-4xl text-navy dark:text-white">Terminology Guide</h1>
        <p className="mt-1 text-sm text-muted max-w-2xl">
          Key financial planning terms used across WealthCraft. Use this page while filling the
          planner or reading reports.
        </p>
      </div>

      <div className="space-y-4">
        {SECTIONS.map((section, i) => (
          <Card key={section.title} className={`animate-fade-up delay-${(i % 3) + 1}`}>
            <CardHeader>
              <CardTitle>{section.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {section.items.map((item) => (
                <div
                  key={item.term}
                  className="border-b border-border/40 pb-3 last:border-0 last:pb-0"
                >
                  <div className="font-semibold text-navy dark:text-white text-sm">{item.term}</div>
                  <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{item.meaning}</p>
                  {item.tip && (
                    <p className="mt-1 text-xs text-teal">Tip: {item.tip}</p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
