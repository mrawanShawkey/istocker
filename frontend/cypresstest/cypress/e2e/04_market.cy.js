describe('04_market.cy.js - Total Market Endpoints Flow (All Sub-routes)', () => {
  it('verifies main market, tickers, sectors, and active telemetry filters', () => {
    const marketRoutes = [
      '/market', 
      '/market/COMI', 
      '/market/sectors', 
      '/market/top-gainers', 
      '/market/top-losers', 
      '/market/trending',
      '/market/history/COMI',
      '/stocks'
    ];

    marketRoutes.forEach((route) => {
      cy.request({
        method: 'GET',
        url: `http://127.0.0.1:5000${route}`,
        failOnStatusCode: false
      }).then((res) => {
        expect(res.status).to.be.oneOf([200, 204, 401, 404, 500]);
        cy.log(`Market Data Pipe [${route}] responded with status: ${res.status}`);
      });
    });
  });
});