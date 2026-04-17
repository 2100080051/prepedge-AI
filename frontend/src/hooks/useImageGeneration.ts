import { useState, useCallback } from 'react';
import { imageGenerationApi } from '@/lib/api';

export const useImageGeneration = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const generate = useCallback(async (prompt: string, imageType?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await imageGenerationApi.generate(prompt, imageType);
      const url = res.data?.image_url;
      setImageUrl(url);
      return url;
    } catch (err: any) {
      const errMsg = err?.response?.data?.detail || err.message || 'Generation failed';
      setError(errMsg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const generateCompanyProfile = useCallback(async (companyName: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await imageGenerationApi.generateCompanyProfile(companyName);
      const url = res.data?.image_url;
      setImageUrl(url);
      return url;
    } catch (err: any) {
      const errMsg = err?.response?.data?.detail || err.message || 'Company generation failed';
      setError(errMsg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const generateBadge = useCallback(async (achievementName: string, style?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await imageGenerationApi.generateBadge(achievementName, style);
      const url = res.data?.image_url;
      setImageUrl(url);
      return url;
    } catch (err: any) {
      const errMsg = err?.response?.data?.detail || err.message || 'Badge generation failed';
      setError(errMsg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { 
    loading, 
    error, 
    imageUrl, 
    setImageUrl,
    generate, 
    generateCompanyProfile, 
    generateBadge 
  };
};
