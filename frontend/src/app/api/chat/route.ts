import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();

    if (!query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }

    // Step 1: Search for relevant chunks from backend
    const searchResponse = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/similarity_search`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          k: 5,
          min_score: 0.25,
        }),
      }
    );

    if (!searchResponse.ok) {
      throw new Error('Failed to search backend');
    }

    const searchData = await searchResponse.json();

    if (searchData.results.length === 0) {
      return NextResponse.json({
        answer: "I couldn't find any relevant information in the research papers to answer your question. Please try rephrasing your question or ask about a different topic.",
        sources: [],
        query,
      });
    }

    // Step 2: Prepare context for OpenAI
    const context = searchData.results
      .map((result: any, index: number) => {
        return `[Source ${index + 1}] ${result.section_heading} (${result.journal}, ${result.publish_year}):
${result.text}`;
      })
      .join('\n\n');

    // Step 3: Generate answer using OpenAI
    const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
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
      }),
    });

    if (!openaiResponse.ok) {
      throw new Error('Failed to generate answer from OpenAI');
    }

    const openaiData = await openaiResponse.json();
    const answer = openaiData.choices[0]?.message?.content || 'I apologize, but I could not generate an answer at this time.';

    return NextResponse.json({
      answer,
      sources: searchData.results,
      query,
    });

  } catch (error) {
    console.error('Chat API error:', error);
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 