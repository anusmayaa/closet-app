import React, { useState } from 'react';
import styles from '../styles/OutfitGenerator.module.css';

const VIBES = [
  { label: 'Formal',      emoji: '🎩' },
  { label: 'Traditional', emoji: '🪷' },
  { label: 'Casual',      emoji: '☀️' },
  { label: 'Gym Wear',    emoji: '🏋️' },
];
const GENDERS = ['Male', 'Female', 'Unisex'];

const OutfitGenerator = ({ onSave }) => {
  const [gender, setGender] = useState('');
  const [vibe, setVibe] = useState('');
  const [outfit, setOutfit] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  const generate = async () => {
    if (!gender || !vibe) { setError('Please select a gender and vibe.'); return; }
    setError(''); setSaved(false); setLoading(true);
    try {
      const res = await fetch(`/generate-outfit?vibe=${encodeURIComponent(vibe)}&gender=${encodeURIComponent(gender)}`);
      if (!res.ok) { setError('Add more clothes to generate this look.'); setOutfit(null); }
      else { setOutfit(await res.json()); }
    } catch { setError('Something went wrong. Try again.'); }
    finally { setLoading(false); }
  };

  const saveToLookbook = async () => {
    const items = Object.values(outfit).filter(Boolean);
    const formData = new FormData();
    formData.append('name', `${vibe} Look`);
    formData.append('vibe', vibe);
    formData.append('gender', gender);
    formData.append('item_ids', items.map(i => i.id).join(','));
    const res = await fetch('/outfits', { method: 'POST', body: formData });
    if (res.ok) { setSaved(true); onSave?.(); }
  };

  const outfitItems = outfit ? Object.entries(outfit).filter(([, v]) => v !== null) : [];

  return (
    <div className={styles.layout}>

      {/* LEFT */}
      <div className={styles.controls}>
        <h2 className={styles.title}>Generate a Look</h2>

        <div className={styles.fieldGroup}>
          <span className={styles.fieldLabel}>Gender</span>
          <div className={styles.genderRow}>
            {GENDERS.map(g => (
              <button key={g}
                className={`${styles.genderBtn} ${gender === g ? styles.genderActive : ''}`}
                onClick={() => setGender(g)}>{g}</button>
            ))}
          </div>
        </div>

        <div className={styles.fieldGroup}>
          <span className={styles.fieldLabel}>Vibe</span>
          <div className={styles.vibeList}>
            {VIBES.map(v => (
              <button key={v.label}
                className={`${styles.vibeBtn} ${vibe === v.label ? styles.vibeActive : ''}`}
                onClick={() => setVibe(v.label)}>
                <span className={styles.vibeEmoji}>{v.emoji}</span>
                <span>{v.label}</span>
              </button>
            ))}
          </div>
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <button className={styles.generateBtn} onClick={generate} disabled={loading}>
          {loading ? 'Generating...' : '✦ Generate Outfit'}
        </button>
      </div>

      {/* RIGHT */}
      <div className={styles.outfitPanel}>
        {!outfit ? (
          <div className={styles.empty}>
            <p className={styles.emptyIcon}>✦</p>
            <p className={styles.emptyText}>Your outfit will appear here</p>
            <p className={styles.emptySubtext}>Select a gender & vibe to get started</p>
          </div>
        ) : (
          <>
            <div className={styles.outfitHeader}>
              <h3 className={styles.outfitTitle}>Your {vibe} Look</h3>
              <div className={styles.outfitBadges}>
                <span className={styles.outfitVibeBadge}>{vibe}</span>
                <span className={styles.outfitGenderBadge}>{gender}</span>
              </div>
            </div>
            <div className={styles.outfitRow}>
              {outfitItems.map(([key, item]) => (
                <div key={key} className={styles.outfitCard}>
                  <img src={item.img_url} alt={item.name} className={styles.outfitImage} />
                  <div className={styles.outfitInfo}>
                    <span className={styles.outfitCategory}>{item.category}</span>
                    <p className={styles.outfitName}>{item.name}</p>
                  </div>
                </div>
              ))}
            </div>
            <button className={styles.saveBtn} onClick={saveToLookbook} disabled={saved}>
              {saved ? '✓ Saved to Lookbook' : '♡ Save to Lookbook'}
            </button>
          </>
        )}
      </div>

    </div>
  );
};

export default OutfitGenerator;
