import React, { useState } from 'react';
import styles from '../styles/UploadForm.module.css';

const CATEGORIES = ['Top', 'Bottom', 'Shoes', 'Dress'];
const VIBES = ['Formal', 'Traditional', 'Casual', 'Gym Wear'];
const GENDERS = ['Male', 'Female', 'Unisex'];

const UploadForm = ({ onUploadSuccess }) => {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [vibe, setVibe] = useState('');
  const [gender, setGender] = useState('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
    }
  };

  const handleSubmit = async () => {
    if (!name || !category || !vibe || !gender || !file) {
      setError('Please fill in all fields and select an image.');
      return;
    }
    setError('');
    setLoading(true);

    const formData = new FormData();
    formData.append('name', name);
    formData.append('category', category);
    formData.append('vibe', vibe);
    formData.append('gender', gender);
    formData.append('file', file);

    try {
      const res = await fetch('/items', {
        method: 'POST',
        body: formData,
      });
      console.log('Status:', res.status);
      const data = await res.json();
      console.log('Response:', data);
      if (res.ok) {
        setName('');
        setCategory('');
        setVibe('');
        setGender('');
        setFile(null);
        setPreview(null);
        onUploadSuccess();
      } else {
        setError(`Server error: ${data.detail || res.status}`);
      }
    } catch (err) {
      setError(`Failed to connect: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.form}>
      <h2 className={styles.title}>Add a piece</h2>

      <label className={styles.imageUpload} htmlFor="fileInput">
        {preview ? (
          <img src={preview} alt="preview" className={styles.preview} />
        ) : (
          <div className={styles.dropzone}>
            <div className={styles.dropIcon}>+</div>
            <span className={styles.dropLabel}>Upload photo</span>
          </div>
        )}
      </label>
      <input
        id="fileInput"
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className={styles.fileInput}
      />

      <div className={styles.fieldGroup}>
        <label className={styles.fieldLabel}>Item Name</label>
        <input
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="e.g. White Linen Shirt"
          className={styles.textInput}
        />
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.fieldLabel}>Category</label>
        <div className={styles.pillSelect}>
          {CATEGORIES.map(c => (
            <button
              key={c}
              className={`${styles.pill} ${category === c ? styles.pillActive : ''}`}
              onClick={() => setCategory(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.fieldLabel}>Vibe</label>
        <div className={styles.pillSelect}>
          {VIBES.map(v => (
            <button
              key={v}
              className={`${styles.pill} ${vibe === v ? styles.pillActive : ''}`}
              onClick={() => setVibe(v)}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.fieldGroup}>
        <label className={styles.fieldLabel}>Gender</label>
        <div className={styles.pillSelect}>
          {GENDERS.map(g => (
            <button
              key={g}
              className={`${styles.pill} ${gender === g ? styles.pillActive : ''}`}
              onClick={() => setGender(g)}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <button
        className={styles.submitBtn}
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? 'Saving...' : 'Save to Closet'}
      </button>
    </div>
  );
};

export default UploadForm;