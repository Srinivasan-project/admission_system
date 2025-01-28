import unittest
from app import create_app, db
from app.models import Application


class ApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_application_submission(self):
        response = self.client.post('/apply', data=dict(
            name='Test Student',
            email='test@student.com',
            academic_background='Test Background',
            degree_certificate=(io.BytesIO(b"fake degree certificate"), 'degree_certificate.pdf'),
            id_proof=(io.BytesIO(b"fake id proof"), 'id_proof.pdf')
        ))
        self.assertEqual(response.status_code, 302)  # Redirect after success
        with self.app.app_context():
            self.assertEqual(Application.query.count(), 1)

    def test_admin_review(self):
        with self.app.app_context():
            application = Application(
                name='Test Student',
                email='test@student.com',
                academic_background='Test Background',
                degree_certificate='degree_certificate.pdf',
                id_proof='id_proof.pdf'
            )
            db.session.add(application)
            db.session.commit()

        response = self.client.get('/admin/review')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Student', response.data)

    def test_application_approval(self):
        with self.app.app_context():
            application = Application(
                name='Test Student',
                email='test@student.com',
                academic_background='Test Background',
                degree_certificate='degree_certificate.pdf',
                id_proof='id_proof.pdf'
            )
            db.session.add(application)
            db.session.commit()
            application_id = application.id

        response = self.client.get(f'/admin/approve/{application_id}')
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            application = Application.query.get(application_id)
            self.assertEqual(application.status, 'Approved')


if __name__ == '__main__':
    unittest.main()
