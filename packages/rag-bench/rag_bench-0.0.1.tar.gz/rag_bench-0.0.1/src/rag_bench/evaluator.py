import numpy as np
from rouge_score import rouge_scorer


class RAGEvaluator:
    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rougeL"], use_stemmer=True
        )

    def evaluate_retrieval(self, retrieved_doc_ids, relevant_doc_id):
        metrics = {}

        # hit rate
        metrics["hit_rate"] = 1.0 if relevant_doc_id in retrieved_doc_ids else 0.0

        # mrr
        for i, doc_id in enumerate(retrieved_doc_ids):
            if doc_id == relevant_doc_id:
                metrics["mrr"] = 1.0 / (i + 1)
                break
        else:
            metrics["mrr"] = 0

        return metrics

    def evaluate_generation(self, generated_answer: str, reference_answer: str):
        rouge_scores = self.rouge_scorer.score(generated_answer, reference_answer)
        return {
            "rouge1": rouge_scores["rouge1"].fmeasure,
            "rougeL": rouge_scores["rougeL"].fmeasure,
        }


def evaluate_rag_results(results, dataset, evaluator: RAGEvaluator):
    evaluation_results = {}

    for i, result in results.items():
        reference_answer = dataset["train"][int(i)]["answer"]

        retrieval_metrics = evaluator.evaluate_retrieval(
            retrieved_doc_ids=result["found_ids"], relevant_doc_id=int(i)
        )

        generation_metrics = evaluator.evaluate_generation(
            generated_answer=result["model_answer"], reference_answer=reference_answer
        )

        evaluation_results[i] = {
            "retrieval": retrieval_metrics,
            "generation": generation_metrics,
        }

    avg_metrics = {"retrieval": {}, "generation": {}}

    for metric in ["hit_rate", "mrr"]:
        avg_metrics["retrieval"][metric] = np.mean(
            [res["retrieval"][metric] for res in evaluation_results.values()]
        )

    for metric in ["rouge1", "rougeL"]:
        avg_metrics["generation"][metric] = np.mean(
            [res["generation"][metric] for res in evaluation_results.values()]
        )

    return {"individual_results": evaluation_results, "average_metrics": avg_metrics}
