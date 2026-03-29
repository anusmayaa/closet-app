import React, { useState, useEffect, useCallback } from 'react';
import styles from '../styles/Lookbook.module.css';

const VIBES = ['All', 'Formal', 'Traditional', 'Casual', 'Gym Wear'];
const GENDERS = ['All', 'Male', 'Female', 'Unisex'];

const Lookbook = ({ onDelete }) => {
  const [outfits, setOutfits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [vibeFilter, setVibeFilter] = useState('All');
  const [genderFilter, setGenderFilter] = useState('All');

  const fetchOutfits = useCallback(async () => {
    setLoading(true);
    const res = await fetch('/outfits');
    if (res.ok) setOutfits(await res.json());
    setLoading(false);
  }, []);

  useEffect(() => { fetchOutfits(); }, [fetchOutfits]);

  const deleteOutfit = async (id) => {
    const res = await fetch(`/outfits/${id}`, { method: 'DELETE' });
    if (res.ok) { setOutfits(prev => prev.filter(o => o.id !== id)); onDelete?.(); }
  };

  const filtered = outfits
    .filter(o => vibeFilter === 'All' || o.vibe === vibeFilter)
    .filter(o => genderFilter === 'All' || o.gender === genderFilter);

  if (loading) return <p className={styles.loading}>Loading lookbook…</p>;

  if (!outfits.length) return (
    <div className={styles.empty}>
      <p className={styles.emptyIcon}>✦</p>
      <p className={styles.emptyText}>Your lookbook is empty</p>
      <p className={styles.emptySubtext}>Save outfits from the generator to see them here</p>
    </div>
  );

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h2 className={styles.title}>My Lookbook</h2>
        <p className={styles.subtitle}>{filtered.length} {filtered.length === 1 ? 'look' : 'looks'}</p>
      </div>

      <div className={styles.filterRow}>
        <span className={styles.filterLabel}>Vibe</span>
        {VIBES.map(v => (
          <button key={v}
            className={`${styles.filterPill} ${vibeFilter === v ? styles.filterPillActive : ''}`}
            onClick={() => setVibeFilter(v)}>{v}</button>
        ))}
        <span className={styles.filterDivider} />
        <span className={styles.filterLabel}>Gender</span>
        {GENDERS.map(g => (
          <button key={g}
            className={`${styles.filterPill} ${genderFilter === g ? styles.filterPillActive : ''}`}
            onClick={() => setGenderFilter(g)}>{g}</button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className={styles.empty}>
          <p className={styles.emptyIcon}>✦</p>
          <p className={styles.emptyText}>No looks match this filter</p>
          <p className={styles.emptySubtext}>Try a different vibe or gender</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {filtered.map(outfit => (
          <div key={outfit.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <div>
                <p className={styles.cardName}>{outfit.name}</p>
                <div className={styles.badges}>
                  <span className={styles.vibeBadge}>{outfit.vibe}</span>
                  {outfit.gender && <span className={styles.genderBadge}>{outfit.gender}</span>}
                </div>
              </div>
              <button className={styles.deleteBtn} onClick={() => deleteOutfit(outfit.id)} title="Remove">✕</button>
            </div>

            <div className={styles.itemsRow}>
              {(outfit.items ?? []).map(item => (
                <div key={item.id} className={styles.itemCard}>
                  <img src={item.img_url} alt={item.name} className={styles.itemImage} />
                  <div className={styles.itemInfo}>
                    <span className={styles.itemCategory}>{item.category}</span>
                    <p className={styles.itemName}>{item.name}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Lookbook;
