import React from 'react';

export default ({color='#8D8D8D', size='24'}) => {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 6C20 3.832 16.337 2 12 2C7.663 2 4 3.832 4 6V8C4 10.168 7.663 12 12 12C16.337 12 20 10.168 20 8V6ZM12 19C7.663 19 4 17.168 4 15V18C4 20.168 7.663 22 12 22C16.337 22 20 20.168 20 18V15C20 17.168 16.337 19 12 19Z" fill={color}/>
      <path d="M20 10C20 12.168 16.337 14 12 14C7.663 14 4 12.168 4 10V13C4 15.168 7.663 17 12 17C16.337 17 20 15.168 20 13V10Z" fill={color}/>
    </svg>
  );
}