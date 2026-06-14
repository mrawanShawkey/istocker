// S — owns result-page text content only.
export const RISK_LABEL_AR = {
  'Conservative Investor':  'مستثمر محافظ',
  'Moderately Conservative':'محافظ إلى حد ما',
  'Balanced Investor':      'مستثمر متوازن',
  'Growth Investor':        'مستثمر للنمو',
  'Aggressive Investor':    'مستثمر قوي',
}

export const RISK_DESC = {
  'Conservative Investor':   { en:'You prefer stability and consistent returns over high-risk growth. Focus on dividend-paying stocks and established companies.', ar:'تفضل الاستقرار والعوائد الثابتة. تركز على الأسهم التي توزع أرباحاً والشركات الراسخة.' },
  'Moderately Conservative': { en:'You seek a balance between stability and moderate growth with limited downside risk.', ar:'تسعى إلى التوازن بين الاستقرار والنمو المعتدل مع محدودية الخسارة.' },
  'Balanced Investor':       { en:'Comfortable with moderate risk, seeking a healthy balance between growth and income.', ar:'مرتاح مع المخاطر المعتدلة ويسعى للتوازن بين النمو والدخل.' },
  'Growth Investor':         { en:'You prioritise capital growth and accept higher volatility for better long-term returns.', ar:'تُولي الأولوية لنمو رأس المال وتقبل تقلبات أعلى.' },
  'Aggressive Investor':     { en:'You seek maximum returns and are comfortable with significant portfolio fluctuations.', ar:'تسعى لأقصى عائد وأنت مرتاح مع التقلبات الكبيرة.' },
}

export const RISK_AI_TEXT = {
  'Conservative Investor':  { en:"Based on your low risk scores and your desire for security, AI has selected defensive stocks and index funds: they don't grow at lighting speed, but protect you from financial shocks and provide stable returns.", ar:"بناءً على درجات المخاطر المنخفضة لديك، اختار الذكاء الاصطناعي أسهماً دفاعية وصناديق مؤشرات توفر عوائد مستقرة." },
  'Moderately Conservative':{ en:"Your profile led AI to select a mix of stable and moderate-growth stocks offering capital protection with some upside.", ar:"دفع ملفك الذكاء الاصطناعي لاختيار مزيج من الأسهم المستقرة ومتوسطة النمو." },
  'Balanced Investor':      { en:"Your balanced profile led AI to select a mix of defensive and growth stocks offering both capital protection and upside potential.", ar:"دفع ملفك المتوازن الذكاء الاصطناعي لاختيار مزيج من الأسهم الدفاعية والنمو." },
  'Growth Investor':        { en:"Your growth profile guided AI toward higher-returning stocks with manageable volatility and strong fundamentals.", ar:"وجّه ملفك الذكاء الاصطناعي نحو أسهم عالية العائد بتقلبات قابلة للإدارة." },
  'Aggressive Investor':    { en:"Your high risk appetite guided AI toward high-growth, high-beta stocks with maximum upside potential. Be prepared for significant volatility.", ar:"شهيتك العالية للمخاطرة وجّهت الذكاء الاصطناعي نحو أسهم عالية النمو. كن مستعداً للتقلبات الكبيرة." },
}

export const DEFAULT_RESULT = { riskCapacity:29, riskTolerance:25, riskLevel:39, label:'Conservative Investor' }

export const NEXT_STEPS = {
  en: [
    'Research each recommended stock further on a financial website.',
    'Open a brokerage account — trusted Egyptian platforms: EFG Hermes · Thndr · CI Capital · Mubasher Trade',
    'Upload your documents: Egyptian National ID, selfie verification, proof of address.',
    'Sign the trading agreement electronically — required by the Egyptian Financial Regulatory Authority.',
    'Receive your investor code — your identification number to trade on the Egyptian Exchange.',
    'Deposit funds via: Bank transfer · Debit card · Mobile wallet.',
    'Start trading: search for a company stock and choose Buy order / Sell order.',
    'Track your portfolio. Return to iStocker anytime for updated predictions and market changes.',
  ],
  ar: [
    'ابحث عن كل سهم موصى به على موقع مالي متخصص.',
    'افتح حساب وساطة — منصات مصرية موثوقة: EFG Hermes · Thndr · CI Capital · Mubasher Trade',
    'ارفع مستنداتك: الهوية الوطنية المصرية، صورة شخصية، إثبات عنوان.',
    'وقّع اتفاقية التداول إلكترونياً — مطلوبة من هيئة الرقابة المالية المصرية.',
    'احصل على رمز المستثمر — رقم تعريفك للتداول في البورصة المصرية.',
    'أودع الأموال عبر: تحويل بنكي · بطاقة خصم · محفظة إلكترونية.',
    'ابدأ التداول: ابحث عن سهم الشركة واختر أمر شراء أو بيع.',
    'تابع محفظتك. عد إلى iStocker في أي وقت للحصول على توقعات وتغيرات السوق.',
  ],
}

export const ONBOARDING_GROUPS = [
  { key:'incomeSituation',      en:'Income Situation',           ar:'وضع الدخل',
    opts:[['no_income','No regular income','لا دخل منتظم'],['irregular','Irregular income','دخل غير منتظم'],['not_guar','Regular, not guaranteed','منتظم غير مضمون'],['stable','Stable monthly income','دخل شهري ثابت'],['very_stable','Very stable income','دخل مستقر جداً']] },
  { key:'savingsDuration',      en:'Savings Duration',           ar:'مدة المدخرات',
    opts:[['lt1','< 1 Month','أقل من شهر'],['1_3','1–3 Months','1–3 أشهر'],['4_6','4–6 Months','4–6 أشهر'],['7_12','7–12 Months','7–12 شهراً'],['gt12','> 12 Months','أكثر من 12 شهراً']] },
  { key:'financialObligations', en:'Financial Obligations',      ar:'الالتزامات المالية',
    opts:[['heavy','Heavy, little flexibility','ثقيلة، مرونة قليلة'],['moderate','Moderate obligations','التزامات معتدلة'],['limited','Limited obligations','التزامات محدودة'],['none','No major obligations','لا التزامات رئيسية']] },
  { key:'investedMoneyAccess',  en:'Access to Invested Money',   ar:'الوصول إلى الأموال المستثمرة',
    opts:[['very_likely','Very likely','مرجح جداً'],['likely','Likely','محتمل'],['not_sure','Not sure','لست متأكداً'],['unlikely','Unlikely','غير مرجح'],['very_unlikely','Very unlikely','غير مرجح جداً']] },
]
