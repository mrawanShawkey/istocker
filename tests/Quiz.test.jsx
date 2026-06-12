// src/__tests__/Quiz.test.jsx
// Tests Quiz page behaviour:
//   • blocks "Next" when no answer is selected (shows toast)
//   • allows "Next" after an answer is selected
//   • Back button is disabled on the first question
//   • progress advances correctly
//   • finishing the last question calls setQuizResult and navigates to /result

import { describe, it, expect, vi } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router-dom'
import Quiz from '../pages/Quiz'
import { renderWithProviders } from '../tests/renderWithProviders'

// Stub the result page so we can assert navigation happened
const ResultPage = () => <div>Result Page</div>

function renderQuiz(opts = {}) {
  return renderWithProviders(
    <Routes>
      <Route path="/quiz"   element={<Quiz />} />
      <Route path="/result" element={<ResultPage />} />
    </Routes>,
    { initialEntries: ['/quiz'], userOverride: { email: 'mona@test.com' }, ...opts }
  )
}

// ── helpers ───────────────────────────────────────────────────────
const clickNext = () => fireEvent.click(screen.getByRole('button', { name: /next/i }))
const clickBack = () => fireEvent.click(screen.getByRole('button', { name: /back/i }))

// Select the first option in a multiple-choice question
function selectFirstOption() {
  const options = screen.getAllByRole('button').filter(
    btn => !['Next →', '← Back', 'Next', 'Back'].some(t => btn.textContent.includes(t))
  )
  if (options.length) fireEvent.click(options[0])
}

// ── blocking navigation ───────────────────────────────────────────
describe('Quiz — blocking navigation without an answer', () => {
  it('shows a toast and does NOT advance when Next is clicked unanswered', async () => {
    renderQuiz()
    clickNext()
    await waitFor(() => {
      expect(
        screen.getByText(/please answer this question to continue/i)
      ).toBeInTheDocument()
    })
  })

  it('does NOT navigate to the next question when the answer is missing', () => {
    renderQuiz()
    // Progress bar / counter starts at question 1
    expect(screen.getByText(/Question 1 of 17/i)).toBeInTheDocument()
    clickNext()
    // Still on question 1
    expect(screen.getByText(/Question 1 of 17/i)).toBeInTheDocument()
  })
})

// ── allowing navigation ───────────────────────────────────────────
describe('Quiz — advancing after answering', () => {
  it('moves to question 2 after selecting an answer and clicking Next', async () => {
    renderQuiz()
    selectFirstOption()
    clickNext()
    await waitFor(() => {
      expect(screen.getByText(/Question 2 of 17/i)).toBeInTheDocument()
    })
  })
})

// ── Back button ───────────────────────────────────────────────────
describe('Quiz — Back button', () => {
  it('is disabled on the first question', () => {
    renderQuiz()
    expect(screen.getByRole('button', { name: /back/i })).toBeDisabled()
  })

  it('is enabled after advancing to question 2', async () => {
    renderQuiz()
    selectFirstOption()
    clickNext()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /back/i })).not.toBeDisabled()
    })
  })

  it('returns to the previous question when clicked', async () => {
    renderQuiz()
    selectFirstOption()
    clickNext()
    await waitFor(() => screen.getByText(/Question 2 of 17/i))
    clickBack()
    expect(screen.getByText(/Question 1 of 17/i)).toBeInTheDocument()
  })
})

// ── Unanswered hint ───────────────────────────────────────────────
describe('Quiz — unanswered hint text', () => {
  it('shows the "Select an answer" hint on question 2+ when unanswered', async () => {
    renderQuiz()
    // Answer Q1 and advance to Q2
    selectFirstOption()
    clickNext()
    await waitFor(() => screen.getByText(/Question 2 of 17/i))
    // Q2 is unanswered — hint should appear (cur > 0 condition in JSX)
    expect(screen.getByText(/select an answer to continue/i)).toBeInTheDocument()
  })

  it('does NOT show the hint on question 1 (even though unanswered)', () => {
    renderQuiz()
    expect(screen.queryByText(/select an answer to continue/i)).not.toBeInTheDocument()
  })
})