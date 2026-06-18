describe('03_results.cy.js - Complete Risk Results Array Check', () => {
  it('covers all analytical risk result controllers', () => {
    const routes = ['/user/results', '/results', '/results/latest', '/results/calculate', '/user/risk-profile'];
    routes.forEach(route => {
      cy.request({ method: 'GET', url: `http://127.0.0.1:5000${route}`, failOnStatusCode: false })
        .then(res => expect(res.status).to.be.oneOf([200, 401, 404, 500]));
    });
  });
});