import json

if __name__ == '__main__':
    for i in range(0, 6):
        sample = []
        for j in range(1, 11):
            index = i * 10 + j
            sample.append({
                "id": index,
                "name": f"Test {index}"
            })
        with open( f"./data/sample_{i+1}.json", "w") as file:
            json.dump(sample, file, indent=4)
