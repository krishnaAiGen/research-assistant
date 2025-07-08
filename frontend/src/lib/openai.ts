import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function generateAnswer(query: string, context: string): Promise<string> {
  try {
    const response = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4',
      messages: [
        {
          role: 'system',
          content: `You are a helpful research assistant. Answer questions based on the provided context from scientific papers and journals. 
          
          Guidelines:
          - Provide accurate, well-structured answers
          - Cite relevant information from the context
          - If the context doesn't contain enough information, say so
          - Keep answers concise but informative
          - Use scientific terminology appropriately`
        },
        {
          role: 'user',
          content: `Context from research papers:
          ${context}
          
          Question: ${query}
          
          Please provide a comprehensive answer based on the context above.`
        }
      ],
      temperature: 0.7,
      max_tokens: 1000,
    });

    return response.choices[0]?.message?.content || 'I apologize, but I could not generate an answer at this time.';
  } catch (error) {
    console.error('OpenAI API error:', error);
    throw new Error('Failed to generate answer from OpenAI');
  }
} 