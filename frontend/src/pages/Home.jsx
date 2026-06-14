// S — Home page: the "about / how it works" page with steps and illustrations.
//     Route: /
import '../styles/home.css'
import WhatIsSection        from '../components/home/WhatIsSection'
import HowItWorksSection    from '../components/home/HowItWorksSection'
import WhySection           from '../components/home/WhySection'
import ModelAccuracySection from '../components/home/ModelAccuracySection'
import HomeCTA              from '../components/home/HomeCTA'

export default function Home() {
  return (
    <div className="home-page">
      <WhatIsSection />
      <HowItWorksSection />
      <WhySection />
      <ModelAccuracySection />
      <HomeCTA />
    </div>
  )
}
