import React from 'react';

export default ({color='#8D8D8D', size='24'}) => {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M7 4H16.4815V8.74074L13.3333 11.8889L16.4815 15.037V19.7778H7V15.037L10.1481 11.8889L7 8.74074V4ZM14.8889 15.4444L11.7407 12.2963L8.59259 15.4444H14.8889ZM8.59259 8.33333H14.8889V5.55556H8.59259V8.33333Z" fill={color}/>
    </svg>
  );
}
