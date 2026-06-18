// Integration Tests: Protected Routes, Token Refresh, Recommendations

const testUser = {
  firstName: 'Route',
  lastName:  'Tester',
  email:     'routetester_cypress@example.com',
  password:  'Password123!',
}

describe('Protected Routes — unauthenticated redirects', () => {
  beforeEach(() => cy.clearLocalStorage())

  it('redirects /profile to /signin', () => {
    cy.visit('/profile')
    cy.url().should('include', '/signin')
  })

  it('redirects /quiz to /signin', () => {
    cy.visit('/quiz')
    cy.url().should('include', '/signin')
  })

  it('redirects /settings to /signin', () => {
    cy.visit('/settings')
    cy.url().should('include', '/signin')
  })

  it('redirects /result to /signin', () => {
    cy.visit('/result')
    cy.url().should('include', '/signin')
  })
})

describe('Protected Routes — authenticated access', () => {
  beforeEach(() => cy.loginViaAPI(testUser))

  it('allows /profile with valid token', () => {
    cy.visit('/profile')
    cy.url().should('include', '/profile')
  })

  it('allows /quiz with valid token', () => {
    cy.visit('/quiz')
    cy.url().should('include', '/quiz')
  })

  it('allows /settings with valid token', () => {
    cy.visit('/settings')
    cy.url().should('include', '/settings')
  })
})

describe('Token Refresh Flow → POST /auth/refresh', () => {
  it('auto-refreshes expired access token and retries original request', () => {
    cy.loginViaAPI(testUser)

    // Simulate expired access token
    cy.window().then(win => {
      win.localStorage.setItem('ist_access_token', 'expired_token_xyz')
    })

    cy.intercept('POST', '**/auth/refresh').as('refresh')

    cy.visit('/profile')

    // apiClient detects 401 TOKEN_EXPIRED and calls /auth/refresh automatically
    cy.wait('@refresh').then(i => {
      expect(i.response.statusCode).to.eq(200)
      expect(i.response.body.data).to.have.property('newAccessToken')
    })

    // New token stored
    cy.window().then(win => {
      expect(win.localStorage.getItem('ist_access_token')).to.not.eq('expired_token_xyz')
    })

    // Profile should still load
    cy.url().should('include', '/profile')
  })
})

describe('Recommendations → GET /recommendations', () => {
  it('returns 404 RESULTS_NOT_FOUND for user who has not answered questionnaire', () => {
    // Register fresh user with no quiz history
    const freshUser = {
      firstName: 'Fresh',
      lastName:  'User',
      email:     `freshuser_${Date.now()}@example.com`,
      password:  'Password123!',
    }
    cy.request({
      method: 'POST',
      url: 'http://localhost:5000/auth/register',
      body: freshUser,
    }).then(res => {
      const token = res.body.data.accessToken
      cy.request({
        method: 'GET',
        url: 'http://localhost:5000/recommendations',
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false,
      }).then(recRes => {
        expect(recRes.status).to.eq(404)
        expect(recRes.body.code).to.eq('RESULTS_NOT_FOUND')
      })
    })
  })
})
