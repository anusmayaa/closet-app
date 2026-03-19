import React from 'react';
import styles from '../styles/Navbar.module.css';

const Navbar = ({ activePage, setActivePage }) => {
  return (
    <nav className={styles.navbar}>
      <div className={styles.logo}>
        <span>f</span>able
      </div>
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activePage === 'wardrobe' ? styles.active : ''}`}
          onClick={() => setActivePage('wardrobe')}
        >
          Wardrobe
        </button>
        <button
          className={`${styles.tab} ${activePage === 'generator' ? styles.active : ''}`}
          onClick={() => setActivePage('generator')}
        >
          Generator
        </button>
        <button
          className={`${styles.tab} ${activePage === 'lookbook' ? styles.active : ''}`}
          onClick={() => setActivePage('lookbook')}
        >
          Lookbook
        </button>
      </div>
    </nav>
  );
};

export default Navbar;