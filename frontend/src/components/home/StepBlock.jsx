// S  — renders a single numbered step row.
// I  — receives only what it needs: stepNumber, title, children, emoji, flip (layout).
import IllustrationBox from './IllustrationBox'

export default function StepBlock({ stepNumber, title, children, emoji, imgSrc, flip = false }) {
  const textBlock = (
    <div className="step-body">
      <div className="step-number-label">Step {stepNumber} :</div>
      {title && <h3>{title} </h3>}
      {children}
    </div>
  )
  /*
    TO ADD IMAGE to any step:
    Pass imgSrc="/assets/step-N.png" to this StepBlock.
    IllustrationBox will automatically render the image instead of the placeholder.
  */
  const illus = <IllustrationBox emoji={emoji} imgSrc={imgSrc} label={`Step ${stepNumber} image`} />

  return (
    <div className={`step-row${flip ? ' step-row--flip' : ''}`}>
      {flip ? <>{illus}{textBlock}</> : <>{textBlock}{illus}</>}
    </div>
  )
}
