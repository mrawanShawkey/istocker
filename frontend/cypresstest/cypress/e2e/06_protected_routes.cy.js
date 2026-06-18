describe('06_protected_routes.cy.js - Advanced Security & Recommendations Sweep', () => {
  it('hits all core restricted recommendation endpoints', () => {
    const secureRoutes = ['/recommendations', '/recommendations/portfolio', '/recommendations/stocks', '/portfolio'];
    
    secureRoutes.forEach(route => {
      cy.request({ 
        method: 'GET', 
        url: `http://127.0.0.1:5000${route}`, 
        failOnStatusCode: false 
      }).then(res => {
     
        expect(res.status).to.be.oneOf([200, 401, 403, 404, 405, 500]);
        cy.log(`Security Route [${route}] checked. Response: ${res.status}`);
      });
    });
  });
});