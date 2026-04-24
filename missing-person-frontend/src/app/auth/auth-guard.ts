import { CanActivateFn } from '@angular/router';

export const policeGuard: CanActivateFn = (route, state) => {
  console.log('PoliceGuard: Checking authentication...');
  
  const token = localStorage.getItem('token');

  if (!token) {
    console.error('PoliceGuard: No token found in localStorage');
    alert('Please login first ❌');
    return false;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    console.log('PoliceGuard: Token payload:', payload);
    console.log('PoliceGuard: role_id:', payload.role_id);

    if (payload.role_id === 2) {
      console.log('PoliceGuard: Access granted ✅');
      return true;
    } else {
      console.error('PoliceGuard: User is not police. role_id =', payload.role_id);
      alert('Access denied: Police access only ❌');
      return false;
    }
  } catch (error) {
    console.error('PoliceGuard: Invalid token format', error);
    alert('Invalid session. Please login again ❌');
    localStorage.removeItem('token');
    localStorage.removeItem('policeUser');
    return false;
  }
};