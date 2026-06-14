
/* data.js — all static content */

export const questionsEN = [
  { type:'opts', q:'Compared to others in Egypt, how would you describe your willingness to take price-change risks when buying Egyptian stocks?', opts:['I want zero risk','I want very little risk','I am okay with low risk','I am average','I am okay with high risk','I like taking very high risk','I want the highest risk for the highest gain'] },
  { type:'opts', q:'If you bought a stock today and its price dropped suddenly tomorrow, how would you handle that?', opts:['Very stressed — sell immediately to save what\'s left','Anxious — check the price every hour','Concerned — wait a few days to see','Calm — remind myself prices go up and down','Not worried at all — stocks are long-term'] },
  { type:'opts', q:'When you think of the word "Risk" in Egyptian stocks, which word comes to mind first?', opts:['Losing money','Uncertainty about what will happen','A chance to make money','Potential for very high profits'] },
  { type:'slider', q:'If you had to choose between a stable job with moderate pay increase or an unstable job with higher pay increase, which would you choose?', l:'Stable job', m:'Not sure', r:'Unstable job' },
  { type:'opts', q:'Facing a major stock purchase decision, you would be more concerned about:', opts:['Avoiding losses first','Checking risks, then gains','Focusing on gains but aware of risks','Profits only'] },
  { type:'slider', q:'How would you feel after spending a large amount of money on a stock?', l:'Very pessimistic', m:'Neutral', r:'Very Optimistic' },
  { type:'opts', q:'If you lost 20% of your portfolio in one month, what would you do?', opts:['Sell everything immediately','Sell some, hold the rest','Hold and wait for recovery','Buy more at lower prices'] },
  { type:'opts', q:'What is your primary investment goal?', opts:['Capital preservation','Regular income','Moderate growth','Aggressive growth'] },
  { type:'slider', q:'How much experience do you have with the stock market?', l:'No experience', m:'Some experience', r:'Very experienced' },
  { type:'opts', q:'What percentage of your savings are you willing to invest in stocks?', opts:['Less than 10%','10–25%','25–50%','More than 50%'] },
  { type:'opts', q:'How long do you plan to keep your investments?', opts:['Less than 1 year','1–3 years','3–7 years','More than 7 years'] },
  { type:'slider', q:'How comfortable are you seeing your portfolio value fluctuate significantly?', l:'Very uncomfortable', m:'Neutral', r:'Very comfortable' },
  { type:'opts', q:'When the market drops 10%, you typically:', opts:['Panic and sell','Feel worried but hold','See it as normal','See it as a buying opportunity'] },
  { type:'opts', q:'Your investment strategy is best described as:', opts:['Very conservative','Conservative','Balanced','Aggressive'] },
  { type:'slider', q:'How important is liquidity (being able to sell quickly) to you?', l:'Not important', m:'Somewhat important', r:'Very important' },
  { type:'opts', q:'How do you feel about borrowing money to invest?', opts:['Never — absolutely not','Only for very safe investments','Sometimes if returns look high','Regularly as a core strategy'] },
  { type:'opts', q:'What best describes your reaction to financial news?', opts:['I avoid it — it makes me anxious','I read it but try not to react','I read it and sometimes adjust strategy','I follow it closely and act quickly'] },
];

export const questionsAR = [
  { type:'opts', q:'مقارنةً بالآخرين في مصر، كيف تصف استعدادك للمخاطرة بتقلبات الأسعار عند شراء الأسهم المصرية؟', opts:['أريد تجربة خالية من المخاطر','أريد مخاطرة قليلة جداً','لا أمانع المخاطر المنخفضة','أنا شخص متوسط','لا أمانع المخاطرة العالية','أحب المخاطرة العالية جداً','أريد أعلى مستوى من المخاطرة لتحقيق أعلى ربح'] },
  { type:'opts', q:'إذا اشتريت سهماً اليوم وانخفض سعره فجأة غداً، كيف ستتعامل مع ذلك؟', opts:['ضغط شديد — البيع الفوري','قلق — التحقق من السعر كل ساعة','قلق — انتظار بضعة أيام','هدوء — أذكر نفسي أن الأسعار ترتفع وتنخفض','لن أقلق أبداً — الأسهم استثمار طويل'] },
  { type:'opts', q:'عندما تفكر في كلمة "المخاطرة" في سياق الأسهم المصرية، ما الكلمة الأولى التي تتبادر إلى ذهنك؟', opts:['خسارة المال','عدم اليقين','فرصة لكسب المال','إمكانية أرباح عالية جداً'] },
  { type:'slider', q:'إذا اخترت بين وظيفة مستقرة بزيادة معتدلة أو وظيفة غير مستقرة بزيادة أعلى، أيهما ستختار؟', l:'وظيفة مستقرة', m:'غير متأكد', r:'وظيفة غير مستقرة' },
  { type:'opts', q:'عند اتخاذ قرار شراء سهم كبير، ما الذي يشغل تفكيرك أكثر؟', opts:['تجنب الخسائر أولاً','فحص المخاطر ثم المكاسب','التركيز على المكاسب مع مراعاة المخاطر','الأرباح فقط'] },
  { type:'slider', q:'كيف ستشعر بعد إنفاق مبلغ كبير على سهم؟', l:'متشائم جداً', m:'محايد', r:'متفائل جداً' },
  { type:'opts', q:'إذا خسرت 20% من محفظتك في شهر واحد، ماذا ستفعل؟', opts:['بيع كل شيء فوراً','بيع البعض والاحتفاظ بالباقي','الانتظار للتعافي','شراء المزيد بأسعار أقل'] },
  { type:'opts', q:'ما هو هدفك الاستثماري الأساسي؟', opts:['الحفاظ على رأس المال','دخل منتظم','نمو معتدل','نمو قوي'] },
  { type:'slider', q:'ما مقدار خبرتك في سوق الأسهم؟', l:'لا خبرة', m:'بعض الخبرة', r:'خبرة واسعة' },
  { type:'opts', q:'ما نسبة مدخراتك المستعد لاستثمارها في الأسهم؟', opts:['أقل من 10%','10–25%','25–50%','أكثر من 50%'] },
  { type:'opts', q:'كم من الوقت تخطط للاحتفاظ باستثماراتك؟', opts:['أقل من سنة','1–3 سنوات','3–7 سنوات','أكثر من 7 سنوات'] },
  { type:'slider', q:'ما مدى راحتك مع تقلبات قيمة محفظتك؟', l:'غير مرتاح جداً', m:'محايد', r:'مرتاح جداً' },
  { type:'opts', q:'عندما ينخفض السوق 10%، أنت عادةً:', opts:['تبيع بذعر','تقلق لكن تحتفظ','تراه أمراً طبيعياً','تراه فرصة شراء'] },
  { type:'opts', q:'تُوصف استراتيجيتك الاستثمارية بأنها:', opts:['محافظة جداً','محافظة','متوازنة','قوية'] },
  { type:'slider', q:'ما أهمية السيولة (البيع السريع) بالنسبة لك؟', l:'غير مهمة', m:'مهمة نوعاً ما', r:'مهمة جداً' },
  { type:'opts', q:'كيف تشعر حيال الاقتراض للاستثمار؟', opts:['لا أبداً','فقط للاستثمارات الآمنة جداً','أحياناً إذا بدت العوائد عالية','بانتظام كاستراتيجية'] },
  { type:'opts', q:'كيف تتعامل مع الأخبار المالية؟', opts:['أتجنبها','أقرأها دون تفاعل','أقرأها وأعدّل أحياناً','أتابعها وأتصرف بسرعة'] },
];

export const STATIC_MARKET = {
  tickers: [
    { name:'Qalaa Holdings', nameAr:'شركة قلعة القابضة', price:3.690, chg:+1.23, pct:+1.10, dir:'up',   predictedPrice:4.150 },
    { name:'Telecom Egypt',  nameAr:'المصرية للاتصالات', price:84.65, chg:+3.41, pct:+0.24, dir:'up',   predictedPrice:91.50 },
    { name:'Palm Hills',     nameAr:'بالم هيلز',          price:8.680, chg:-3.20, pct:-0.94, dir:'down', predictedPrice:9.45 },
    { name:'Juhayna Food',   nameAr:'شركة جهينة',         price:26.80, chg:-13.91,pct:-0.22, dir:'down', predictedPrice:28.50 },
  ],
  chart: {
    labels:['1 Jan','5 Jan','10 Jan','15 Jan','20 Jan','25 Jan','30 Jan'],
    values:[20000,21500,25000,31000,42000,52000,58000],
  },
  movers: [
    { code:'TMGH', name:'Talaat Mostafa Group',        price:145.60, pct:+2.39, dir:'up' },
    { code:'FWRY', name:'Fawry',                        price:32.80,  pct:+3.80, dir:'up' },
    { code:'ORAS', name:'Orascom Construction',         price:328.50, pct:+1.61, dir:'up' },
    { code:'COMI', name:'Commercial International Bank',price:78.50,  pct:+1.10, dir:'up' },
    { code:'CCAP', name:'Credit Agricole Egypt',        price:86.20,  pct:-1.26, dir:'down' },
  ],
  sectors: [
    { name:'Real Estate',    nameAr:'العقارات',           stocks:['TMGH','PHDC','CIRA'], pct:+1.88 },
    { name:'Finance',        nameAr:'تمويل',              stocks:['COMI','CCAP','EKHO'], pct:+0.58 },
    { name:'Technology',     nameAr:'تكنولوجيا',          stocks:['FWRY','RAYA'],        pct:+2.45 },
    { name:'Consumer Goods', nameAr:'السلع الاستهلاكية',  stocks:['EAST','JUFO'],        pct:+0.32 },
    { name:'Construction',   nameAr:'البناء',              stocks:['ORAS','ARAB'],        pct:+1.12 },
  ],
};

export const RECOMMENDATIONS = {
  'Conservative Investor':   [
    { code:'TMGH', name:'Talaat Mostafa Group', nameAr:'مجموعة طلعت مصطفى', sector:'Real Estate', price:145.60, chg:+2.39, desc:"Egypt's largest listed real estate developer. High growth with moderate volatility and stable dividends.", descAr:'أكبر شركة تطوير عقاري مدرجة في مصر. نمو عالٍ مع تقلبات معتدلة وأرباح مستقرة.' },
    { code:'FWRY', name:'Fawry', nameAr:'فوري', sector:'Technology', price:32.80, chg:+3.80, desc:"Egypt's leading digital payment platform. Strong fintech growth in an expanding digital economy.", descAr:'منصة الدفع الرقمي الرائدة في مصر. نمو قوي في اقتصاد رقمي متوسع.' },
    { code:'RAYA', name:'Raya Contact Center', nameAr:'راية', sector:'Technology', price:5.65, chg:+4.60, desc:'Leading BPO with growing regional presence, technology integration, and expanding commercial operations.', descAr:'شركة رائدة في مجال خدمات الأعمال مع حضور إقليمي متنامٍ وتكامل تكنولوجي.' },
  ],
  'Moderately Conservative': [
    { code:'COMI', name:'CIB Egypt', nameAr:'البنك التجاري الدولي', sector:'Finance', price:78.50, chg:+1.10, desc:"Egypt's premier private-sector bank with strong fundamentals and a consistent dividend history.", descAr:'أبرز بنك خاص في مصر بأسس متينة وتاريخ ثابت في توزيع الأرباح.' },
    { code:'TMGH', name:'Talaat Mostafa Group', nameAr:'مجموعة طلعت مصطفى', sector:'Real Estate', price:145.60, chg:+2.39, desc:'Diversified real estate developer with stable track record and strong project pipeline.', descAr:'مطور عقاري متنوع بسجل حافل وخطة مشاريع قوية.' },
    { code:'EAST', name:'Eastern Company', nameAr:'الشركة الشرقية', sector:'Consumer', price:18.90, chg:+0.80, desc:'Monopoly manufacturer with stable cash flows and consistent dividend payments quarter after quarter.', descAr:'شركة محتكرة بتدفقات نقدية مستقرة وتوزيعات أرباح منتظمة.' },
  ],
  'Balanced Investor': [
    { code:'ORAS', name:'Orascom Construction', nameAr:'أوراسكوم للإنشاءات', sector:'Construction', price:328.50, chg:+1.61, desc:'Regional construction leader benefiting from MENA infrastructure mega-projects and government contracts.', descAr:'شركة إنشاءات إقليمية رائدة تستفيد من المشاريع الكبرى في منطقة الشرق الأوسط وشمال أفريقيا.' },
    { code:'FWRY', name:'Fawry', nameAr:'فوري', sector:'Technology', price:32.80, chg:+3.80, desc:'High-growth fintech with expanding merchant network and increasing penetration of Egypt\'s digital economy.', descAr:'شركة تقنية مالية عالية النمو بشبكة تجار متوسعة واختراق متزايد للاقتصاد الرقمي المصري.' },
    { code:'CCAP', name:'Credit Agricole Egypt', nameAr:'كريدي أجريكول', sector:'Finance', price:86.20, chg:-1.26, desc:'Well-capitalised bank with solid retail banking franchise and a growing SME lending portfolio.', descAr:'بنك مُرسمل جيداً بامتياز مصرفي للأفراد قوي ومحفظة إقراض متنامية للشركات الصغيرة.' },
  ],
  'Growth Investor': [
    { code:'FWRY', name:'Fawry', nameAr:'فوري', sector:'Technology', price:32.80, chg:+3.80, desc:'High-growth digital payments play with significant untapped market penetration potential.', descAr:'رهان على مدفوعات رقمية عالية النمو مع إمكانات اختراق سوقية ضخمة.' },
    { code:'ORAS', name:'Orascom Construction', nameAr:'أوراسكوم', sector:'Construction', price:328.50, chg:+1.61, desc:"Infrastructure giant set to benefit from Egypt's national development plan and Gulf project pipelines.", descAr:'عملاق البنية التحتية الجاهز للاستفادة من خطة التنمية الوطنية المصرية.' },
    { code:'TMGH', name:'Talaat Mostafa Group', nameAr:'طلعت مصطفى', sector:'Real Estate', price:145.60, chg:+2.39, desc:'Real estate bellwether with aggressive land-bank expansion and strong brand recognition.', descAr:'الشركة المرجعية للعقارات بتوسع قوي في بنك الأراضي وحضور قوي للعلامة التجارية.' },
  ],
  'Aggressive Investor': [
    { code:'RAYA', name:'Raya Contact Center', nameAr:'راية', sector:'Technology', price:5.65, chg:+4.60, desc:'High-beta tech play with meaningful upside from regional BPO market and digital transformation wave.', descAr:'سهم تقني ذو معامل بيتا مرتفع مع صعود كبير من سوق الـ BPO الإقليمي.' },
    { code:'PHDC', name:'Palm Hills', nameAr:'بالم هيلز', sector:'Real Estate', price:8.68, chg:-0.94, desc:'High-growth developer targeting premium residential segments with aggressive land acquisition strategy.', descAr:'مطور عقاري عالي النمو يستهدف الشريحة السكنية الراقية باستراتيجية اقتناء أراضٍ قوية.' },
    { code:'FWRY', name:'Fawry', nameAr:'فوري', sector:'Technology', price:32.80, chg:+3.80, desc:'Fintech disruptor with high volatility and compelling long-term growth story in Egypt\'s digital economy.', descAr:'مُعطِّل في مجال التكنولوجيا المالية مع قصة نمو طويلة الأجل في الاقتصاد الرقمي المصري.' },
  ],
};

export function scoreQuiz(answers) {
  const W = [1.5,1.2,1.0,1.3,1.0,1.2,1.4,1.0,0.8,1.0,1.1,1.0,1.3,1.2,0.7,1.0,0.9];
  let tol = 0, cap = 0;
  answers.forEach((a, i) => {
    const norm = (typeof a==='number'?a:0)/6;
    const w = W[i]||1;
    if (i < 10) tol += norm * w * 100;
    else         cap += norm * w * 100;
  });
  const riskTolerance = Math.min(100, Math.round(tol/10));
  const riskCapacity  = Math.min(100, Math.round(cap/7));
  const riskLevel     = Math.round(riskTolerance*0.6 + riskCapacity*0.4);
  let label;
  if (riskLevel<=30)     label='Conservative Investor';
  else if(riskLevel<=50) label='Moderately Conservative';
  else if(riskLevel<=70) label='Balanced Investor';
  else if(riskLevel<=85) label='Growth Investor';
  else                   label='Aggressive Investor';
  return { riskTolerance, riskCapacity, riskLevel, label };
}
