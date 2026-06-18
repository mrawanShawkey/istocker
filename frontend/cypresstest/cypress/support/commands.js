Cypress.Commands.add('loginViaAPI', (email, password) => {
  cy.request({
    method: 'POST',
    url: 'http://127.0.0.1:5000/auth/login', // Real Flask API
    body: { email, password },
    failOnStatusCode: false
  }).then((response) => {
    if (response.status === 200 && response.body.tokens) {
      // Real tokens storage keys standard layout
      localStorage.setItem('ist_access_token', response.body.tokens.accessToken);
      localStorage.setItem('ist_refresh_token', response.body.tokens.refreshToken);
    }
  });
});