import styled from 'styled-components'

export const Nav = styled.aside`
  height: 100%;
  width: calc(100vw / 5);
  padding-top: 16px;
  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;
  background-color: var(--color-secondary);
  overflow-x: hidden;
  border-right: 1px solid var(--color-support-secondary);
`;

export const NavItem = styled.a`
  display: flex;
  align-items: center;
  padding: 8px 16px;
  text-decoration: none;

  p {
    padding: 8px 0;
    padding-left: 32px;
    font-size: 14px;
    color: var(--color-typography);
    font-weight: 500;
  }

  p:hover {
    color: var(--color-primary);
  }
`;