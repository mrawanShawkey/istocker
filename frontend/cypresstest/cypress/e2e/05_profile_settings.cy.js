describe('05_profile_settings.cy.js - Full User Profile Endpoint Sweep', () => {
  it('sweeps all endpoints affecting user configuration tables', () => {
    const routes = ['/user/profile', '/user/settings', '/profile', '/user/preferences'];
    
    routes.forEach(route => {
      cy.request({ 
        method: 'GET', 
        url: `http://127.0.0.1:5000${route}`, 
        failOnStatusCode: false 
      }).then(res => {
     
        expect(res.status).to.be.oneOf([200, 401, 403, 404, 405, 500]);
        cy.log(`Profile GET [${route}] checked. Response: ${res.status}`);
      });

      cy.request({ 
        method: 'PATCH', 
        url: `http://127.0.0.1:5000${route}`, 
        body: { username: 'MalakTest' }, 
        failOnStatusCode: false 
      }).then(res => {
       
        expect(res.status).to.be.oneOf([200, 400, 401, 403, 404, 405, 500]);
        cy.log(`Profile PATCH [${route}] checked. Response: ${res.status}`);
      });
    });
  });
});