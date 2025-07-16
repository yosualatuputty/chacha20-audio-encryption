import unittest
import os
import shutil
from app import app, UPLOAD_FOLDER, get_user_upload_folder, clear_user_uploads

class MultiUserSessionTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists(UPLOAD_FOLDER):
            shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(UPLOAD_FOLDER)

    def test_multi_user_folder_isolation(self):
        # Simulasi folder user A
        client_a = app.test_client()
        with client_a.session_transaction() as sess_a:
            sess_a['user_folder'] = 'user_a_session'
        with client_a:
            folder_a = os.path.join(UPLOAD_FOLDER, 'user_a_session')
            os.makedirs(folder_a, exist_ok=True)
            with open(os.path.join(folder_a, 'dummy.txt'), 'w') as f:
                f.write("dummy A")

        # Simulasi folder user B
        client_b = app.test_client()
        with client_b.session_transaction() as sess_b:
            sess_b['user_folder'] = 'user_b_session'
        with client_b:
            folder_b = os.path.join(UPLOAD_FOLDER, 'user_b_session')
            os.makedirs(folder_b, exist_ok=True)
            with open(os.path.join(folder_b, 'dummy.txt'), 'w') as f:
                f.write("dummy B")

        # Panggil clear untuk user A saja
        clear_user_uploads('user_a_session')

        # Validasi hasil
        self.assertFalse(os.path.exists(folder_a))
        self.assertTrue(os.path.exists(folder_b))

if __name__ == '__main__':
    unittest.main()
