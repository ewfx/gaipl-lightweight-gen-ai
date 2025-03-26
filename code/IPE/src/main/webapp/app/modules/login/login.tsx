import React, { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';

import { useAppDispatch, useAppSelector } from 'app/config/store';
import { login } from 'app/shared/reducers/authentication';
import LoginModal from './login-modal';

export const Login = () => {
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector(state => state.authentication.isAuthenticated);
  const loginError = useAppSelector(state => state.authentication.loginError);
  const showModalLogin = useAppSelector(state => state.authentication.showModalLogin);
  const [showModal, setShowModal] = useState(showModalLogin);
  const navigate = useNavigate();

  useEffect(() => {
    setShowModal(true);
  }, []);

  const handleLogin = (username, password, rememberMe = false) => dispatch(login(username, password, rememberMe));

  const handleClose = () => {
    setShowModal(false);
    navigate('/'); // Show public home screen when login is closed
  };

  // ✅ After successful login → always go to /incident
  if (isAuthenticated) {
    return <Navigate to="/incident" replace />;
  }

  return <LoginModal showModal={showModal} handleLogin={handleLogin} handleClose={handleClose} loginError={loginError} />;
};

export default Login;
