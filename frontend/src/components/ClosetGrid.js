import React, { useEffect, useState } from 'react';
import styles from '../styles/ClosetGrid.module.css';

const VIBES = ['All', 'Formal', 'Traditional', 'Casual', 'Gym Wear'];
const GENDERS = ['All', 'Male', 'Female', 'Unisex'];

const ClosetGrid = ({ refresh }) => {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState('All');
  const [genderFilter, setGenderFilter] = useState('All');

  useEffect(() => {
    fetch('/items')
      .then(r => r.json())
      .then(data => setItems(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, [refresh]);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    await fetch(`/items/${id}`, { method: 'DELETE' });
    setItems(prev => prev.filter(i => i.id !== id));
  };

  const filtered = items
    .filter(i => filter === 'All' || i.vibe.split(',').map(v => v.trim()).includes(filter))
    .filter(i => genderFilter === 'All' || i.gender === genderFilter);

  return (
    <div className={styles.gridWrapper}>
      <div className={styles.filterRow}>
        <span className={styles.filterLabel}>Vibe</span>
        {VIBES.map(v => (
          <button
            key={v}
            className={`${styles.filterPill} ${filter === v ? styles.filterPillActive : ''}`}
            onClick={() => setFilter(v)}
          >{v}</button>
        ))}
        <span className={styles.filterDivider} />
        <span className={styles.filterLabel}>Gender</span>
        {GENDERS.map(g => (
          <button
            key={g}
            className={`${styles.filterPill} ${genderFilter === g ? styles.filterPillActive : ''}`}
            onClick={() => setGenderFilter(g)}
          >{g}</button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>🧥</div>
          <p className={styles.emptyText}>{items.length === 0 ? 'Your closet is empty' : 'No items for this vibe'}</p>
          <p className={styles.emptySubtext}>{items.length === 0 ? 'Add a piece to get started' : 'Try a different filter'}</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {filtered.map(item => (
            <div key={item.id} className={styles.card}>
              <img src={item.img_url} alt={item.name} className={styles.cardImage} />
              <button className={styles.deleteBtn} onClick={e => handleDelete(item.id, e)}>✕</button>
              <div className={styles.cardInfo}>
                <p className={styles.cardName}>{item.name}</p>
                <div className={styles.cardBadges}>
                  <span className={styles.badge}>{item.category}</span>
                  {item.vibe.split(',').map(v => (
                    <span key={v} className={styles.badge}>{v.trim()}</span>
                  ))}
                  <span className={styles.badge}>{item.gender}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ClosetGrid;
