// S — Single Responsibility: all educational content data lives here.
// O — Open/Closed: add new levels or videos by extending these arrays — no component changes needed.

export const LEVELS = [
  { id: 'beginner',  icon: '👤', en: 'Beginner',      ar: 'مبتدئ'       },
  { id: 'mid',       icon: '👥', en: 'Mid-Level',     ar: 'متوسط'       },
  { id: 'advanced',  icon: '🏆', en: 'Advanced Level', ar: 'متقدم'       },
]

// Each level has a list of video lessons.
// videoUrl: a YouTube embed URL or local path.
// thumbUrl: thumbnail shown before play (optional — falls back to placeholder).
export const LESSONS = {
  beginner: [
    {
      id: 'b1',
      en: { title: 'What is the Stock Market?',      desc: 'Learn the basics of how stock markets work and why they matter.' },
      ar: { title: 'ما هو سوق الأسهم؟',              desc: 'تعرّف على أساسيات كيفية عمل أسواق الأسهم وأهميتها.' },
      videoUrl: 'https://www.youtube.com/embed/p7HKvqRI_Bo',
      duration: '8:24',
    },
    {
      id: 'b2',
      en: { title: 'How to Buy Your First Stock',    desc: 'A step-by-step guide to purchasing stocks for the first time on the Egyptian exchange.' },
      ar: { title: 'كيف تشتري أول سهم لك',           desc: 'دليل خطوة بخطوة لشراء الأسهم لأول مرة في البورصة المصرية.' },
      videoUrl: 'https://www.youtube.com/embed/86rPNPmBVpE',
      duration: '11:05',
    },
    {
      id: 'b3',
      en: { title: 'Understanding Risk & Return',    desc: 'Discover the relationship between risk and potential profit in investing.' },
      ar: { title: 'فهم المخاطرة والعائد',            desc: 'اكتشف العلاقة بين المخاطرة والربح المحتمل في الاستثمار.' },
      videoUrl: 'https://www.youtube.com/embed/R2hO1TFBCpY',
      duration: '9:10',
    },
  ],
  mid: [
    {
      id: 'm1',
      en: { title: 'Reading a Stock Chart',          desc: 'Understand candlestick patterns, trends, and key technical indicators.' },
      ar: { title: 'قراءة مخطط السهم',               desc: 'افهم أنماط الشموع والاتجاهات والمؤشرات الفنية الرئيسية.' },
      videoUrl: 'https://www.youtube.com/embed/CMrg_MI4V18',
      duration: '14:30',
    },
    {
      id: 'm2',
      en: { title: 'Fundamental Analysis Basics',    desc: 'How to evaluate a company\'s financial health before investing.' },
      ar: { title: 'أساسيات التحليل الأساسي',        desc: 'كيف تقيّم الصحة المالية للشركة قبل الاستثمار.' },
      videoUrl: 'https://www.youtube.com/embed/OGBNUl8VCFQ',
      duration: '16:45',
    },
    {
      id: 'm3',
      en: { title: 'Building a Diversified Portfolio', desc: 'Strategies to spread risk across different sectors and asset types.' },
      ar: { title: 'بناء محفظة متنوعة',               desc: 'استراتيجيات لتوزيع المخاطر عبر قطاعات وأنواع أصول مختلفة.' },
      videoUrl: 'https://www.youtube.com/embed/fwe-PkrNe4I',
      duration: '12:55',
    },
  ],
  advanced: [
    {
      id: 'a1',
      en: { title: 'Technical Analysis Deep Dive',   desc: 'Advanced chart patterns, Fibonacci levels, and momentum strategies.' },
      ar: { title: 'التحليل الفني المتعمق',           desc: 'أنماط المخططات المتقدمة ومستويات فيبوناتشي واستراتيجيات الزخم.' },
      videoUrl: 'https://www.youtube.com/embed/eynxyoKgpng',
      duration: '22:18',
    },
    {
      id: 'a2',
      en: { title: 'Options & Derivatives',           desc: 'Introduction to options trading and how derivatives affect the market.' },
      ar: { title: 'الخيارات والمشتقات',              desc: 'مقدمة لتداول الخيارات وكيف تؤثر المشتقات على السوق.' },
      videoUrl: 'https://www.youtube.com/embed/YNvBPVRTnxI',
      duration: '19:40',
    },
    {
      id: 'a3',
      en: { title: 'Quantitative Trading Strategies', desc: 'Data-driven models and algorithmic approaches to stock selection.' },
      ar: { title: 'استراتيجيات التداول الكمي',       desc: 'النماذج القائمة على البيانات والمناهج الخوارزمية لاختيار الأسهم.' },
      videoUrl: 'https://www.youtube.com/embed/s-N2ovuqmJY',
      duration: '24:00',
    },
  ],
}
