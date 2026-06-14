// S — Educational Content page: hero + video/lesson card + CTA.
//     Route: /education
import '../styles/home.css'
import '../styles/education.css'
import HeroSection        from '../components/home/HeroSection'
import StockMarketSection from '../components/education/StockMarketSection'
import HomeCTA            from '../components/home/HomeCTA'

export default function Education() {
  return (
    <div className="home-page">
      <HeroSection />
      <StockMarketSection />
      <HomeCTA />
    </div>
  )
}
