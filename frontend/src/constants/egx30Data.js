// S — Single Responsibility: all EGX 30 company data in one place.
// O — Add a company or edit a description here; no component changes needed.

export const EGX30_COMPANIES = [
  { code:'COMI',  name:'Commercial International Bank', nameAr:'البنك التجاري الدولي',
    price:78.50,  open:77.20,  high:79.10,  low:76.80,  chg:+1.30,  pct:+1.68, dir:'up',   sector:'Finance',
    desc:"Egypt's largest private-sector bank with a strong retail and corporate loan portfolio. Known for consistent profitability and dividend growth.",
    descAr:'أكبر بنك خاص في مصر بمحفظة قوية من القروض التجزئة والشركات. معروف بالربحية المتسقة ونمو الأرباح الموزعة.' ,
    predictedPrice:82.3 },

  { code:'TMGH',  name:'Talaat Mostafa Group',           nameAr:'مجموعة طلعت مصطفى',
    price:145.60, open:142.50, high:146.80, low:141.90, chg:+3.10,  pct:+2.18, dir:'up',   sector:'Real Estate',
    desc:"Egypt's largest real-estate developer with mega projects. High growth potential with moderate volatility.",
    descAr:'أكبر مطور عقاري في مصر مع مشاريع ضخمة. إمكانات نمو عالية مع تقلبات معتدلة.' ,
    predictedPrice:158.4 },

  { code:'HRHO',  name:'EFG Hermes',                     nameAr:'هيرميس',
    price:38.20,  open:37.50,  high:38.90,  low:37.10,  chg:+0.70,  pct:+1.87, dir:'up',   sector:'Finance',
    desc:'Leading investment bank and financial services group in the MENA region, covering brokerage, asset management, and investment banking.',
    descAr:'مجموعة خدمات مالية ومصرفية استثمارية رائدة في منطقة الشرق الأوسط وشمال أفريقيا.' ,
    predictedPrice:41.5 },

  { code:'FWRY',  name:'Fawry',                          nameAr:'فوري',
    price:32.80,  open:31.60,  high:33.20,  low:31.40,  chg:+1.20,  pct:+3.80, dir:'up',   sector:'Technology',
    desc:"Egypt's leading digital payments platform processing millions of bill payments daily. Strong growth driver in Egypt's fintech ecosystem.",
    descAr:'منصة المدفوعات الرقمية الرائدة في مصر. محرك نمو قوي في منظومة التكنولوجيا المالية المصرية.' ,
    predictedPrice:37.2 },

  { code:'EKHO',  name:'EK Holding',                     nameAr:'إي كي القابضة',
    price:11.45,  open:11.20,  high:11.60,  low:11.05,  chg:+0.25,  pct:+2.23, dir:'up',   sector:'Finance',
    desc:'Diversified financial holding company with interests in leasing, microfinance, and insurance across Egypt and Africa.',
    descAr:'شركة قابضة مالية متنوعة تعمل في التأجير والتمويل الأصغر والتأمين في مصر وأفريقيا.' ,
    predictedPrice:12.8 },

  { code:'ORAS',  name:'Orascom Construction',           nameAr:'أوراسكوم للإنشاء',
    price:328.50, open:323.00, high:330.20, low:321.50, chg:+5.50,  pct:+1.73, dir:'up',   sector:'Construction',
    desc:'Global engineering and construction company with major infrastructure projects across the Middle East, Africa, and the United States.',
    descAr:'شركة هندسة وإنشاء عالمية بمشاريع بنية تحتية ضخمة في الشرق الأوسط وأفريقيا والولايات المتحدة.' ,
    predictedPrice:348.0 },

  { code:'PHDC',  name:'Palm Hills Development',         nameAr:'بالم هيلز للتعمير',
    price:8.68,   open:8.95,   high:9.10,   low:8.60,   chg:-0.27,  pct:-2.93, dir:'down', sector:'Real Estate',
    desc:'Mid-to-premium residential real-estate developer focusing on gated communities in Greater Cairo and the North Coast.',
    descAr:'مطور عقاري سكني يركز على المجمعات المسوّرة في القاهرة الكبرى والساحل الشمالي.' ,
    predictedPrice:9.45 },

  { code:'ORWE',  name:'Orascom Investment Holding',     nameAr:'أوراسكوم للاستثمار',
    price:1.24,   open:1.28,   high:1.30,   low:1.22,   chg:-0.04,  pct:-3.03, dir:'down', sector:'Finance',
    desc:'Holding company with diversified investments in hospitality, tourism, and real-estate assets mainly in North Africa and the Middle East.',
    descAr:'شركة قابضة باستثمارات متنوعة في الضيافة والسياحة والعقارات في شمال أفريقيا والشرق الأوسط.' ,
    predictedPrice:1.38 },

  { code:'EFIH',  name:'EFG Finance Holding',            nameAr:'هيرميس القابضة للتمويل',
    price:17.80,  open:17.50,  high:18.10,  low:17.30,  chg:+0.30,  pct:+1.72, dir:'up',   sector:'Finance',
    desc:'Non-bank financial services platform under the EFG umbrella, offering consumer finance, mortgage lending, and microfinance products.',
    descAr:'منصة خدمات مالية غير مصرفية تحت مظلة EFG، تقدم تمويل المستهلكين والرهن العقاري والتمويل الأصغر.' ,
    predictedPrice:19.6 },

  { code:'RAYA',  name:'Raya Holding',                   nameAr:'راية القابضة',
    price:35.60,  open:34.80,  high:36.10,  low:34.60,  chg:+0.80,  pct:+2.30, dir:'up',   sector:'Technology',
    desc:'Egyptian technology and outsourcing conglomerate with subsidiaries in IT distribution, contact-centre services, and digital transformation.',
    descAr:'تكتل التكنولوجيا والاستعانة بمصادر خارجية مع شركات تابعة في توزيع تقنية المعلومات وخدمات مراكز الاتصال.' ,
    predictedPrice:38.9 },

  { code:'EAST',  name:'Eastern Company',                nameAr:'الشركة الشرقية للدخان',
    price:48.90,  open:48.20,  high:49.50,  low:48.00,  chg:+0.70,  pct:+1.47, dir:'up',   sector:'Consumer',
    desc:"Egypt's dominant tobacco manufacturer with a near-monopoly on cigarette production. Stable cash flows and regular dividend distribution.",
    descAr:'الشركة المسيطرة على إنتاج السجائر في مصر. تدفقات نقدية مستقرة وتوزيع منتظم للأرباح.' ,
    predictedPrice:52.4 },

  { code:'JUFO',  name:'Juhayna Food Industries',        nameAr:'جهينة للصناعات الغذائية',
    price:26.80,  open:27.50,  high:27.80,  low:26.60,  chg:-0.70,  pct:-2.47, dir:'down', sector:'Consumer',
    desc:'Leading dairy and juice manufacturer in Egypt. Strong brand recognition with wide distribution across domestic retail channels.',
    descAr:'شركة رائدة في تصنيع الألبان والعصائر في مصر. حضور قوي في قنوات التوزيع المحلية.' ,
    predictedPrice:28.5 },

  { code:'EGTS',  name:'Egyptian Resorts',               nameAr:'المنتجعات المصرية',
    price:3.42,   open:3.38,   high:3.50,   low:3.35,   chg:+0.04,  pct:+1.19, dir:'up',   sector:'Real Estate',
    desc:'Developer of the Sahl Hasheesh resort on the Red Sea coast. Long-term land bank with tourism and hospitality potential.',
    descAr:'مطور منتجع سهل حشيش على ساحل البحر الأحمر. احتياطي أراضٍ طويل الأجل مع إمكانات في السياحة والضيافة.' ,
    predictedPrice:3.75 },

  { code:'CCAP',  name:'Credit Agricole Egypt',          nameAr:'كريدي أجريكول مصر',
    price:86.20,  open:87.30,  high:87.80,  low:85.90,  chg:-1.10,  pct:-1.25, dir:'down', sector:'Finance',
    desc:'Subsidiary of the French banking giant Crédit Agricole. Offers retail, corporate, and private banking services across Egypt.',
    descAr:'فرع المجموعة المصرفية الفرنسية كريدي أجريكول. يقدم خدمات مصرفية للأفراد والشركات في مصر.' ,
    predictedPrice:90.1 },

  { code:'ARAB',  name:'Arab Cotton Ginning',            nameAr:'العربية لحليج الأقطان',
    price:7.85,   open:7.70,   high:7.95,   low:7.65,   chg:+0.15,  pct:+1.95, dir:'up',   sector:'Construction',
    desc:'Industrial company specialising in cotton ginning, storage, and logistics services in the Nile Delta region of Egypt.',
    descAr:'شركة صناعية متخصصة في حليج القطن والتخزين والخدمات اللوجستية في منطقة دلتا النيل.' ,
    predictedPrice:8.4 },

  { code:'SWDY',  name:'El Sewedy Electric',             nameAr:'السويدي إليكتريك',
    price:22.50,  open:22.10,  high:22.80,  low:21.90,  chg:+0.40,  pct:+1.83, dir:'up',   sector:'Industrial',
    desc:'Integrated energy solutions provider covering cables, transformers, smart metering, and renewable energy projects across 120 countries.',
    descAr:'مزود حلول طاقة متكاملة يغطي الكابلات والمحولات وقياس الطاقة الذكية والطاقة المتجددة في 120 دولة.' ,
    predictedPrice:24.8 },

  { code:'MNHD',  name:'Medinet Nasr Housing',           nameAr:'مدينة نصر للإسكان',
    price:19.30,  open:18.90,  high:19.60,  low:18.80,  chg:+0.40,  pct:+2.16, dir:'up',   sector:'Real Estate',
    desc:'State-affiliated real-estate developer managing residential and commercial units in the Nasr City district of Cairo.',
    descAr:'مطور عقاري مرتبط بالدولة يدير وحدات سكنية وتجارية في حي مدينة نصر بالقاهرة.' ,
    predictedPrice:21.2 },

  { code:'ETEL',  name:'Telecom Egypt',                  nameAr:'المصرية للاتصالات',
    price:84.65,  open:81.20,  high:85.50,  low:80.90,  chg:+3.45,  pct:+4.44, dir:'up',   sector:'Telecom',
    desc:"Egypt's national fixed-line and data network operator. Owns major infrastructure assets including subsea cables and the WE mobile brand.",
    descAr:'مشغل الشبكة الوطنية للخطوط الأرضية والبيانات في مصر. تمتلك أصول بنية تحتية رئيسية تشمل الكابلات البحرية وعلامة WE.' ,
    predictedPrice:91.5 },

  { code:'CLHO',  name:'Cleopatra Hospital',             nameAr:'مستشفيات كليوباترا',
    price:24.60,  open:24.20,  high:25.00,  low:24.00,  chg:+0.40,  pct:+1.66, dir:'up',   sector:'Healthcare',
    desc:'Private hospital network with multiple facilities across Cairo. Benefiting from growing demand for quality private healthcare.',
    descAr:'شبكة مستشفيات خاصة بمرافق متعددة في القاهرة. تستفيد من الطلب المتزايد على الرعاية الصحية الخاصة.' ,
    predictedPrice:27.1 },

  { code:'ACGC',  name:'Arab Ceramics',                  nameAr:'السيراميك والبورسلين',
    price:13.20,  open:13.50,  high:13.60,  low:13.10,  chg:-0.30,  pct:-2.17, dir:'down', sector:'Industrial',
    desc:'Producer of ceramic and porcelain tiles for construction markets. Sensitive to real-estate cycles and raw material costs.',
    descAr:'منتج بلاط السيراميك والبورسلين لأسواق البناء. حساس لدورات العقارات وتكاليف المواد الخام.' ,
    predictedPrice:14.0 },

  { code:'ABUK',  name:'Abu Kir Fertilizers',            nameAr:'أبو قير للأسمدة',
    price:189.40, open:187.00, high:190.50, low:186.50, chg:+2.40,  pct:+1.28, dir:'up',   sector:'Industrial',
    desc:'One of Egypt\'s largest nitrogen fertiliser producers. Benefits from subsidised natural gas inputs and strong agricultural demand.',
    descAr:'أحد أكبر منتجي الأسمدة النيتروجينية في مصر. يستفيد من مدخلات الغاز الطبيعي المدعومة والطلب الزراعي القوي.' ,
    predictedPrice:198.0 },

  { code:'OCDI',  name:'Orascom Development',            nameAr:'أوراسكوم للتطوير',
    price:14.90,  open:15.20,  high:15.40,  low:14.80,  chg:-0.30,  pct:-1.94, dir:'down', sector:'Real Estate',
    desc:'Integrated resort developer operating hotels, residential units, and leisure facilities across Egypt, UAE, Switzerland, and Oman.',
    descAr:'مطور منتجعات متكاملة يشغل فنادق ووحدات سكنية ومرافق ترفيهية في مصر والإمارات وسويسرا وعُمان.' ,
    predictedPrice:16.2 },

  { code:'SKPC',  name:'Sidi Kerir Petrochemicals',      nameAr:'سيدي كرير للبتروكيماويات',
    price:12.30,  open:12.10,  high:12.50,  low:12.00,  chg:+0.20,  pct:+1.65, dir:'up',   sector:'Energy',
    desc:'Petrochemical company producing ethylene and polyethylene at its Alexandria complex. Earnings closely tied to global oil and polymer prices.',
    descAr:'شركة بتروكيماويات تنتج الإيثيلين والبولي إيثيلين في مجمعها بالإسكندرية. الأرباح مرتبطة بأسعار النفط العالمية.' ,
    predictedPrice:13.5 },

  { code:'HELI',  name:'Heliopolis Housing',             nameAr:'مدينة مصر للإسكان',
    price:6.75,   open:6.60,   high:6.85,   low:6.55,   chg:+0.15,  pct:+2.27, dir:'up',   sector:'Real Estate',
    desc:'State-linked developer managing residential and commercial properties in the historic Heliopolis district in eastern Cairo.',
    descAr:'مطور مرتبط بالدولة يدير عقارات سكنية وتجارية في حي مصر الجديدة التاريخي في شرق القاهرة.' ,
    predictedPrice:7.3 },

  { code:'AMOC',  name:'Alexandria Mineral Oils',        nameAr:'إسكو للمعادن',
    price:28.40,  open:28.80,  high:29.00,  low:28.20,  chg:-0.40,  pct:-1.37, dir:'down', sector:'Energy',
    desc:'Refinery and lubricant oil producer based in Alexandria. Revenue driven by petroleum product margins and export volumes.',
    descAr:'مصفاة ومنتج زيوت تشحيم في الإسكندرية. الإيرادات مدفوعة بهوامش المنتجات البترولية وأحجام التصدير.' ,
    predictedPrice:29.8 },

  { code:'ISPH',  name:'Ibnsina Pharma',                 nameAr:'ابن سينا للأدوية',
    price:42.30,  open:41.80,  high:42.80,  low:41.60,  chg:+0.50,  pct:+1.21, dir:'up',   sector:'Healthcare',
    desc:"Egypt's largest pharmaceutical distributor, supplying hospitals, pharmacies and clinics with a broad portfolio of medicines and medical devices.",
    descAr:'أكبر موزع أدوية في مصر يزود المستشفيات والصيدليات والعيادات بمحفظة واسعة من الأدوية والأجهزة الطبية.' ,
    predictedPrice:45.6 },

  { code:'LCSW',  name:'Lecico Egypt',                   nameAr:'ليسيكو مصر',
    price:9.10,   open:9.30,   high:9.40,   low:9.00,   chg:-0.20,  pct:-2.11, dir:'down', sector:'Industrial',
    desc:'Manufacturer of sanitary ware and ceramic products sold domestically and exported to European and regional markets.',
    descAr:'شركة تصنيع أدوات صحية ومنتجات سيراميك تُباع محلياً وتُصدَّر إلى الأسواق الأوروبية والإقليمية.' ,
    predictedPrice:9.8 },

  { code:'NCGR',  name:'National Corp for Construct.',   nameAr:'الوطنية للبناء',
    price:5.40,   open:5.30,   high:5.50,   low:5.25,   chg:+0.10,  pct:+1.89, dir:'up',   sector:'Construction',
    desc:'Contractor and construction company involved in housing, infrastructure, and government mega-project delivery across Egypt.',
    descAr:'مقاول وشركة إنشاءات مشاركة في المساكن والبنية التحتية وتسليم المشاريع الحكومية الكبرى في مصر.' ,
    predictedPrice:5.85 },

  { code:'CIEB',  name:'CIB Egypt',                      nameAr:'بنك CIB',
    price:82.10,  open:80.50,  high:82.80,  low:80.20,  chg:+1.60,  pct:+2.00, dir:'up',   sector:'Finance',
    desc:"One of Egypt's top-performing private banks with a focus on corporate and SME lending, digital banking, and retail financial services.",
    descAr:'أحد أفضل البنوك الخاصة أداءً في مصر مع التركيز على إقراض الشركات والمشروعات الصغيرة والخدمات المصرفية الرقمية.' ,
    predictedPrice:86.4 },

  { code:'DSCW',  name:'Dice Sport & Casual Wear',       nameAr:'دايس للملابس الرياضية',
    price:4.20,   open:4.35,   high:4.40,   low:4.15,   chg:-0.15,  pct:-3.45, dir:'down', sector:'Consumer',
    desc:'Egyptian sportswear and casual clothing manufacturer operating across retail outlets in major cities. Exposed to consumer spending trends.',
    descAr:'شركة تصنيع ملابس رياضية وكاجوال مصرية تعمل في متاجر بالمدن الرئيسية. مرتبطة باتجاهات الإنفاق الاستهلاكي.' ,
    predictedPrice:4.55 },
]

// S — chart generation logic separate from static data
function generateIntraday(open, close) {
  const labels = ['9:30','10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30','14:00','14:30','15:00']
  const steps  = labels.length
  const values = []
  let current  = open
  for (let i = 0; i < steps; i++) {
    const progress = i / (steps - 1)
    const target   = open + (close - open) * progress
    const noise    = (Math.random() - 0.48) * Math.abs(close - open) * 0.4
    current        = target + noise
    values.push(parseFloat(current.toFixed(2)))
  }
  values[values.length - 1] = close
  return { labels, values }
}

export const EGX30_CHARTS  = EGX30_COMPANIES.reduce((acc, c) => {
  acc[c.code] = generateIntraday(c.open, c.price)
  return acc
}, {})

export const EGX30_SECTORS = ['All', ...new Set(EGX30_COMPANIES.map(c => c.sector))]
