import React from 'react';

export default ({color='#8D8D8D', size='24'}) => {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M19 13H13V19H11V13H5V11H11V5H13V11H19V13Z" fill={color}/>
    </svg>
  );
}