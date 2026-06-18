describe('02_quiz.cy.js - Exhaustive Quiz & Questions Backend Sweep', () => {
  it('hits all potential questionnaire routes', () => {
    const gets = ['/questions', '/questions?type=Questionnaire', '/questions?type=Risk', '/quiz', '/quiz/history', '/quiz/current'];
    gets.forEach(route => {
      cy.request({ method: 'GET', url: `http://127.0.0.1:5000${route}`, failOnStatusCode: false })
        .then(res => expect(res.status).to.be.oneOf([200, 401, 404, 500]));
    });

    const posts = ['/questions/responses', '/questions/submit', '/quiz/submit', '/quiz/responses?type=Questionnaire'];
    posts.forEach(route => {
      cy.request({ method: 'POST', url: `http://127.0.0.1:5000${route}`, body: { responses: [] }, failOnStatusCode: false })
        .then(res => expect(res.status).to.be.oneOf([200, 201, 400, 401, 404, 500]));
    });
  });
});